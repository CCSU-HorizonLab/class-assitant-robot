"""V2 auth, role, admin, and teacher API routes."""
from __future__ import annotations

import hashlib
import hmac
import secrets
import smtplib
import ssl
import uuid
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, Response, status
from ..config import settings
from ..utils.security import create_access_token, decode_access_token, hash_password, verify_password
from ..schemas.auth import (
    AISummaryRequest,
    ClassroomBindRequest,
    ClassroomCreateRequest,
    LoginRequest,
    RegisterRequest,
    StatusUpdateRequest,
    UserCreateRequest,
    UserUpdateRequest,
)



router = APIRouter(prefix="/api")
pages_router = APIRouter()

from fastapi.responses import HTMLResponse, RedirectResponse
from ..views import build_login_html, build_register_html


from ..schemas import (
    LoginRequest,
    RegisterRequest,
    EmailCodeRequest,
    UserCreateRequest,
    StatusUpdateRequest,
    AISummaryRequest,
)


AUTH_COOKIE_NAME = "auth_token"


def _normalize_username(username: str) -> str:
    normalized = (username or "").strip()
    if len(normalized) < 3:
        raise HTTPException(status_code=422, detail="username must be at least 3 characters")
    if len(normalized) > 64:
        raise HTTPException(status_code=422, detail="username must be at most 64 characters")
    if not all(ch.isalnum() or ch in {"_", "-", ".", "@"} for ch in normalized):
        raise HTTPException(status_code=422, detail="username can only contain letters, numbers, _, -, ., @")
    return normalized


def _normalize_email(email: str) -> str:
    normalized = (email or "").strip().lower()
    if len(normalized) > 120 or "@" not in normalized:
        raise HTTPException(status_code=422, detail="valid QQ email is required")
    local, _, domain = normalized.partition("@")
    if not local or domain != "qq.com":
        raise HTTPException(status_code=422, detail="only QQ email registration is supported")
    if not local.replace(".", "").replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=422, detail="invalid QQ email format")
    return normalized


def _validate_register_password(password: str, confirm_password: str) -> None:
    if password != confirm_password:
        raise HTTPException(status_code=422, detail="password confirmation does not match")
    if len(password) < 8:
        raise HTTPException(status_code=422, detail="password must be at least 8 characters")
    if not any(ch.isalpha() for ch in password) or not any(ch.isdigit() for ch in password):
        raise HTTPException(status_code=422, detail="password must contain letters and numbers")


def _normalize_optional_text(value: Optional[str], fallback: Optional[str] = None) -> Optional[str]:
    normalized = (value or "").strip()
    return normalized or fallback


def _verification_code_hash(email: str, code: str) -> str:
    message = f"{email}:{code.strip()}".encode("utf-8")
    secret = settings.jwt_secret.encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _smtp_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_port and settings.smtp_username and settings.smtp_password and settings.smtp_from)


def _send_email_verification_code(email: str, code: str) -> None:
    if not _smtp_configured():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SMTP is not configured")

    message = EmailMessage()
    message["Subject"] = "智能课堂平台注册验证码"
    message["From"] = settings.smtp_from
    message["To"] = email
    message.set_content(
        "\n".join(
            [
                "你正在注册智能课堂行为分析与教学反馈平台教师账号。",
                f"验证码：{code}",
                f"有效期：{settings.email_code_expire_minutes} 分钟。",
                "如果不是你本人操作，请忽略本邮件。",
            ]
        )
    )

    if settings.smtp_use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds, context=context) as server:
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)


def _issue_login_token(user: Dict[str, Any], response: Response) -> Dict[str, Any]:
    token = create_access_token(
        subject=str(user["user_id"]),
        claims={"username": user["username"], "role": user["role"]},
    )
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
    )
    public_user = _user_public(user)
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": public_user,
        "redirect_to": "/admin" if public_user["role"] == "admin" else "/teacher",
    }


def _database_url() -> str:
    database_url = settings.database_url.strip()
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL database URL is required for V2 auth APIs",
        )
    return database_url


def _connect():
    return psycopg2.connect(_database_url())


def _get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    user_id::text AS user_id,
                    username,
                    display_name,
                    password_hash,
                    role,
                    is_active
                FROM users
                WHERE username = %s
                """,
                (username,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None


def _get_user_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    user_id::text AS user_id,
                    username,
                    display_name,
                    role,
                    is_active
                FROM users
                WHERE user_id::text = %s
                """,
                (str(user_id),),
            )
            row = cursor.fetchone()
            return dict(row) if row else None


def _user_public(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "user_id": str(user.get("user_id") or ""),
        "username": user.get("username") or "",
        "display_name": user.get("display_name") or user.get("username") or "",
        "role": user.get("role") or "",
    }


def _token_from_inputs(auth_token: Optional[str], authorization: Optional[str]) -> Optional[str]:
    if auth_token:
        return auth_token
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer "):].strip()
    return None


def _user_from_token(token: str) -> Dict[str, Any]:
    payload = decode_access_token(token)
    user = _get_user_by_user_id(str(payload["sub"]))
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid user")
    return _user_public(user)


def _get_current_user(
    auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    token = _token_from_inputs(auth_token, authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing auth token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _user_from_token(token)


def _optional_current_user(
    auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME),
    authorization: Optional[str] = Header(default=None),
) -> Optional[Dict[str, Any]]:
    token = _token_from_inputs(auth_token, authorization)
    if not token:
        return None
    try:
        return _user_from_token(token)
    except Exception:
        return None


def _require_admin(current_user: Dict[str, Any] = Depends(_get_current_user)) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin role required")
    return current_user


def _require_teacher(current_user: Dict[str, Any] = Depends(_get_current_user)) -> Dict[str, Any]:
    if current_user.get("role") not in {"teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="teacher role required")
    return current_user


def require_page_user(
    auth_token: Optional[str],
    required_role: Optional[str] = None,
) -> Dict[str, Any]:
    if not auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="login required")
    user = _user_from_token(auth_token)
    if required_role == "admin" and user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin role required")
    if required_role == "teacher" and user.get("role") not in {"teacher", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="teacher role required")
    return user


def optional_page_user(auth_token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not auth_token:
        return None
    try:
        return _user_from_token(auth_token)
    except Exception:
        return None


@router.post("/auth/login", tags=["Auth"])
def login(request: LoginRequest, response: Response) -> Dict[str, Any]:
    user = _get_user_by_username(_normalize_username(request.username))
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return _issue_login_token(user, response)


@router.post("/auth/send-register-code", tags=["Auth"])
def send_register_code(request: EmailCodeRequest) -> Dict[str, Any]:
    email = _normalize_email(request.email)
    now = datetime.now(timezone.utc)
    cooldown_after = now - timedelta(seconds=settings.email_code_cooldown_seconds)

    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT 1 FROM users WHERE lower(email) = lower(%s) LIMIT 1", (email,))
            if cursor.fetchone():
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
            cursor.execute(
                """
                SELECT created_at
                FROM auth_email_verification_codes
                WHERE email = %s AND purpose = 'register'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (email,),
            )
            latest = cursor.fetchone()
            if latest and latest.get("created_at") and latest["created_at"] > cooldown_after:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="please wait before requesting another code")

            code = f"{secrets.randbelow(1000000):06d}"
            expires_at = now + timedelta(minutes=settings.email_code_expire_minutes)
            cursor.execute(
                """
                INSERT INTO auth_email_verification_codes (email, code_hash, purpose, expires_at)
                VALUES (%s, %s, 'register', %s)
                """,
                (email, _verification_code_hash(email, code), expires_at),
            )

    _send_email_verification_code(email, code)
    return {"success": True, "email": email, "expires_in_seconds": settings.email_code_expire_minutes * 60}


@router.post("/auth/register", tags=["Auth"])
def register(request: RegisterRequest) -> Dict[str, Any]:
    username = _normalize_username(request.username)
    email = _normalize_email(request.email)
    _validate_register_password(request.password, request.confirm_password)
    display_name = _normalize_optional_text(request.display_name, fallback=username)
    classroom_id = _normalize_optional_text(request.classroom_id)
    classroom_name = _normalize_optional_text(request.classroom_name, fallback=classroom_id)
    code_hash = _verification_code_hash(email, request.verification_code)

    try:
        with _connect() as connection:
            with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT 1 FROM users WHERE username = %s LIMIT 1", (username,))
                if cursor.fetchone():
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")
                cursor.execute("SELECT 1 FROM users WHERE lower(email) = lower(%s) LIMIT 1", (email,))
                if cursor.fetchone():
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
                cursor.execute(
                    """
                    SELECT id, attempts
                    FROM auth_email_verification_codes
                    WHERE email = %s
                      AND purpose = 'register'
                      AND used_at IS NULL
                      AND expires_at > now()
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (email,),
                )
                verification = cursor.fetchone()
                if not verification:
                    raise HTTPException(status_code=422, detail="verification code is missing or expired")
                if verification.get("attempts", 0) >= 5:
                    raise HTTPException(status_code=422, detail="verification code attempts exceeded")
                cursor.execute(
                    """
                    SELECT id
                    FROM auth_email_verification_codes
                    WHERE id = %s AND code_hash = %s
                    """,
                    (verification["id"], code_hash),
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "UPDATE auth_email_verification_codes SET attempts = attempts + 1 WHERE id = %s",
                        (verification["id"],),
                    )
                    raise HTTPException(status_code=422, detail="verification code is invalid")

                cursor.execute(
                    """
                    INSERT INTO users (user_id, username, email, email_verified, display_name, password_hash, role, is_active)
                    VALUES (%s::uuid, %s, %s, TRUE, %s, %s, 'teacher', TRUE)
                    RETURNING user_id::text AS user_id, username, email, display_name, role, is_active, created_at
                    """,
                    (str(uuid.uuid4()), username, email, display_name, hash_password(request.password)),
                )
                user = dict(cursor.fetchone())
                cursor.execute(
                    "UPDATE auth_email_verification_codes SET used_at = now() WHERE id = %s",
                    (verification["id"],),
                )
                if classroom_id:
                    cursor.execute(
                        """
                        INSERT INTO teacher_classrooms (user_id, classroom_id, classroom_name)
                        VALUES (%s::uuid, %s, %s)
                        ON CONFLICT (user_id, classroom_id) DO UPDATE SET
                            classroom_name = EXCLUDED.classroom_name
                        """,
                        (user["user_id"], classroom_id, classroom_name or classroom_id),
                    )
    except psycopg2.errors.UniqueViolation as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists") from exc

    return {
        "success": True,
        "user": _user_public(user),
        "redirect_to": "/login",
        "message": "registration completed, please login",
    }


@router.get("/auth/me", tags=["Auth"])
def current_user(current_user: Dict[str, Any] = Depends(_get_current_user)) -> Dict[str, Any]:
    return {"success": True, "user": current_user}


@router.post("/auth/logout", tags=["Auth"])
def logout(response: Response) -> Dict[str, Any]:
    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
    return {"success": True}


@router.post("/admin/users", tags=["Admin API"])
def create_user(request: UserCreateRequest, _: Dict[str, Any] = Depends(_require_admin)) -> Dict[str, Any]:
    if request.role not in {"teacher", "admin"}:
        raise HTTPException(status_code=422, detail="role must be teacher or admin")

    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO users (user_id, username, password_hash, role, display_name)
                VALUES (%s::uuid, %s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    role = EXCLUDED.role,
                    display_name = EXCLUDED.display_name,
                    is_active = TRUE
                RETURNING user_id::text AS user_id, username, display_name, role, is_active, created_at
                """,
                (str(uuid.uuid4()), request.username, hash_password(request.password), request.role, request.username),
            )
            user = dict(cursor.fetchone())
            if request.classroom_id:
                cursor.execute(
                    """
                    INSERT INTO teacher_classrooms (user_id, classroom_id, classroom_name)
                    VALUES (%s::uuid, %s, %s)
                    ON CONFLICT (user_id, classroom_id) DO UPDATE SET
                        classroom_name = EXCLUDED.classroom_name
                    """,
                    (
                        user["user_id"],
                        request.classroom_id,
                        request.classroom_name or request.classroom_id,
                    ),
                )
    return {"success": True, "user": user}


@router.get("/admin/users", tags=["Admin API"])
def list_users(_: Dict[str, Any] = Depends(_require_admin)) -> Dict[str, Any]:
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT u.user_id::text AS user_id, u.username, u.display_name, u.role, u.is_active, u.created_at,
                       COALESCE(json_agg(tc.classroom_id) FILTER (WHERE tc.classroom_id IS NOT NULL), '[]') AS classrooms
                FROM users u
                LEFT JOIN teacher_classrooms tc ON tc.user_id = u.user_id
                GROUP BY u.user_id, u.username, u.display_name, u.role, u.is_active, u.created_at
                ORDER BY u.created_at
                """
            )
            users = [dict(row) for row in cursor.fetchall()]
    return {"success": True, "users": users}


# ── Admin: user management (update / deactivate) ──────────────────────────

@router.patch("/admin/users/{user_id}", tags=["Admin API"])
def update_user(
    user_id: str,
    request: "UserUpdateRequest",
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    """Update user fields: display_name, role, is_active, or password."""
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id::text = %s", (user_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="user not found")

            updates: list[str] = []
            params: list[Any] = []

            if request.display_name is not None:
                updates.append("display_name = %s")
                params.append(request.display_name)
            if request.role is not None:
                if request.role not in {"teacher", "admin"}:
                    raise HTTPException(status_code=422, detail="role must be teacher or admin")
                updates.append("role = %s")
                params.append(request.role)
            if request.is_active is not None:
                updates.append("is_active = %s")
                params.append(request.is_active)
            if request.password is not None:
                updates.append("password_hash = %s")
                params.append(hash_password(request.password))

            if not updates:
                raise HTTPException(status_code=400, detail="no fields to update")

            params.append(user_id)
            cursor.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE user_id::text = %s RETURNING user_id::text AS user_id, username, display_name, role, is_active, created_at",
                params,
            )
            user = dict(cursor.fetchone())
    return {"success": True, "user": user}


@router.delete("/admin/users/{user_id}", tags=["Admin API"])
def delete_user(
    user_id: str,
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    """Soft-delete a user by deactivating them."""
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT 1 FROM users WHERE user_id::text = %s", (user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="user not found")
            cursor.execute(
                "UPDATE users SET is_active = FALSE WHERE user_id::text = %s",
                (user_id,),
            )
    return {"success": True, "message": "user deactivated"}


# ── Admin: classroom management (CRUD) ────────────────────────────────────

@router.post("/admin/classrooms", tags=["Admin API"])
def create_classroom(
    request: "ClassroomCreateRequest",
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    """Create or update a classroom entry."""
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO classrooms (classroom_id, name, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (classroom_id) DO UPDATE SET name = EXCLUDED.name
                RETURNING id, classroom_id, name, created_at
                """,
                (request.classroom_id, request.classroom_name or request.classroom_id, datetime.now(timezone.utc)),
            )
            classroom = dict(cursor.fetchone())
    return {"success": True, "classroom": classroom}


@router.post("/admin/classrooms/bind", tags=["Admin API"])
def bind_classroom_teacher(
    request: "ClassroomBindRequest",
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    """Bind (or rebind) a teacher to a classroom."""
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO classrooms (classroom_id, name, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (classroom_id) DO NOTHING
                """,
                (request.classroom_id, request.classroom_name or request.classroom_id, datetime.now(timezone.utc)),
            )
            cursor.execute(
                """
                INSERT INTO teacher_classrooms (user_id, classroom_id, classroom_name)
                VALUES (%s::uuid, %s, %s)
                ON CONFLICT (user_id, classroom_id) DO UPDATE SET classroom_name = EXCLUDED.classroom_name
                """,
                (request.user_id, request.classroom_id, request.classroom_name or request.classroom_id),
            )
    return {"success": True, "message": "classroom bound to teacher"}


@router.delete("/admin/teacher-classrooms", tags=["Admin API"])
def unbind_classroom_teacher(
    user_id: str = Query(...),
    classroom_id: str = Query(...),
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    """Remove a teacher-classroom binding."""
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "DELETE FROM teacher_classrooms WHERE user_id::text = %s AND classroom_id = %s",
                (user_id, classroom_id),
            )
    return {"success": True, "message": "binding removed"}


@router.delete("/admin/classrooms/{classroom_id}", tags=["Admin API"])
def delete_classroom(
    classroom_id: str,
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    """Delete a classroom and its teacher bindings."""
    with _connect() as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("DELETE FROM teacher_classrooms WHERE classroom_id = %s", (classroom_id,))
            cursor.execute("DELETE FROM classrooms WHERE classroom_id = %s", (classroom_id,))
    return {"success": True, "message": "classroom deleted"}


@router.get("/teacher/sessions", tags=["Teacher API"])
def teacher_sessions(current_user: Dict[str, Any] = Depends(_require_teacher)) -> Dict[str, Any]:
    from ..main import repository

    sessions = repository.get_teacher_sessions(current_user["user_id"])
    return {"success": True, "sessions": sessions}


@router.get("/teacher/sessions/{analysis_id}", tags=["Teacher API"])
def teacher_session_detail(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    if hasattr(repository, "get_teacher_session_detail"):
        session = repository.get_teacher_session_detail(
            current_user["user_id"],
            analysis_id,
            is_admin=current_user.get("role") == "admin",
        )
    else:
        session = None
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return {"success": True, "session": session}


@router.get("/teacher/trends", tags=["Teacher API"])
def teacher_trends(
    classroom_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    data_source: str = Query(default="real"),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    if not hasattr(repository, "get_phase3_teacher_trends"):
        return {"success": True, "filters": {"data_source": data_source or "real"}, "overview": {}, "series": {}, "stage_distribution": {}, "risk_lessons": [], "recommendations": [], "data_quality": {}}
    return repository.get_phase3_teacher_trends(
        user_id=user_id,
        classroom_id=classroom_id,
        date_from=date_from,
        date_to=date_to,
        data_source=data_source,
        limit=limit,
    )


@router.get("/teacher/reports", tags=["Teacher API"])
def teacher_reports(
    classroom_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    data_source: str = Query(default="real"),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    if not hasattr(repository, "get_phase3_teacher_reports"):
        return {"success": True, "filters": {"data_source": data_source or "real"}, "items": [], "total": 0}
    return repository.get_phase3_teacher_reports(
        user_id=user_id,
        classroom_id=classroom_id,
        date_from=date_from,
        date_to=date_to,
        data_source=data_source,
        limit=limit,
    )


@router.get("/teacher/reports/detail", tags=["Teacher API"])
def teacher_report_detail(
    result_id: str,
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    if not hasattr(repository, "get_phase3_teacher_report_detail"):
        raise HTTPException(status_code=404, detail="report not found")
    report = repository.get_phase3_teacher_report_detail(result_id=result_id, user_id=user_id)
    if report is None:
        raise HTTPException(status_code=404, detail="report not found")
    return {"success": True, "report": report}


@router.post("/teacher/reports/ai-summary", tags=["Teacher API"])
def teacher_report_ai_summary(
    request: AISummaryRequest,
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..services.ai_report_service import generate_ai_summary
    from ..main import repository

    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    if not hasattr(repository, "get_phase3_teacher_report_detail"):
        raise HTTPException(status_code=404, detail="report not found")
    report = repository.get_phase3_teacher_report_detail(result_id=request.result_id, user_id=user_id)
    if report is None:
        raise HTTPException(status_code=404, detail="report not found")
    ai_summary = generate_ai_summary(report)
    return {"success": ai_summary.get("status") != "failed", "ai_summary": ai_summary}


@router.get("/teacher/results/recent", tags=["Teacher API"])
def teacher_results_recent(
    limit: int = Query(default=10, ge=1, le=100),
    classroom_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    if status not in (None, "", "raw", "reviewed", "archived"):
        raise HTTPException(status_code=400, detail="status must be raw, reviewed, or archived")
    if not hasattr(repository, "get_workbench_recent"):
        return {
            "success": True,
            "limit": limit,
            "classroom_id": classroom_id,
            "status": status,
            "fallback_to_sample": False,
            "items": [],
        }
    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    items = repository.get_workbench_recent(limit=limit, classroom_id=classroom_id, status=status, user_id=user_id)
    return {
        "success": True,
        "limit": limit,
        "classroom_id": classroom_id,
        "status": status,
        "fallback_to_sample": False,
        "items": items,
    }


@router.get("/teacher/classrooms", tags=["Teacher API"])
def teacher_classrooms(current_user: Dict[str, Any] = Depends(_require_teacher)) -> Dict[str, Any]:
    from ..main import repository

    if not hasattr(repository, "get_workbench_classrooms"):
        return {"success": True, "items": []}
    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    return {"success": True, "items": repository.get_workbench_classrooms(user_id=user_id)}


@router.get("/teacher/overview", tags=["Teacher API"])
def teacher_overview(current_user: Dict[str, Any] = Depends(_require_teacher)) -> Dict[str, Any]:
    from ..main import repository

    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    if not hasattr(repository, "get_teacher_overview"):
        return {
            "success": True,
            "teacher": {"id": None, "username": "demo_teacher", "display_name": "Demo Teacher", "role": "teacher"},
            "metrics": {
                "classroom_count": 0,
                "total_result_count": 0,
                "recent_result_count": 0,
                "raw_count": 0,
                "reviewed_count": 0,
                "archived_count": 0,
                "avg_feedback_score": None,
                "avg_attention_score": None,
                "avg_response_score": None,
            },
            "latest_results": [],
            "classroom_summaries": [],
            "todo_items": [],
        }
    return repository.get_teacher_overview(user_id=user_id)


def _parse_days(days: Optional[str]) -> Optional[int]:
    if days in (None, "", "all"):
        return None
    try:
        value = int(str(days))
    except ValueError:
        raise HTTPException(status_code=400, detail="days must be 7, 30, or all")
    if value <= 7:
        return 7
    if value <= 30:
        return 30
    return None


@router.get("/teacher/results", tags=["Teacher API"])
def teacher_results(
    classroom_id: Optional[str] = None,
    status: Optional[str] = None,
    days: Optional[str] = Query(default="30"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    if status not in (None, "", "raw", "reviewed", "archived"):
        raise HTTPException(status_code=400, detail="status must be raw, reviewed, or archived")
    parsed_days = _parse_days(days)
    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    if not hasattr(repository, "get_teacher_results"):
        return {
            "success": True,
            "filters": {
                "classroom_id": classroom_id or "",
                "status": status or "",
                "days": parsed_days,
                "limit": limit,
                "offset": offset,
            },
            "items": [],
            "total": 0,
        }
    return repository.get_teacher_results(
        user_id=user_id,
        classroom_id=classroom_id,
        status=status,
        days=parsed_days,
        limit=limit,
        offset=offset,
    )


@router.get("/admin/overview", tags=["Admin API"])
def admin_overview(_: Dict[str, Any] = Depends(_require_admin)) -> Dict[str, Any]:
    from ..main import repository

    if not hasattr(repository, "get_admin_overview"):
        return {
            "success": True,
            "admin": {"id": None, "username": "demo_admin", "display_name": "Demo Admin", "role": "admin"},
            "metrics": {
                "teacher_count": 0,
                "classroom_count": 0,
                "result_count": 0,
                "recent_result_count": 0,
                "today_result_count": 0,
                "raw_count": 0,
                "reviewed_count": 0,
                "archived_count": 0,
                "avg_feedback_score": None,
                "avg_attention_score": None,
                "avg_response_score": None,
            },
            "system_status": {
                "cloud_service": "ok",
                "database": "unavailable",
                "latest_upload_at": None,
                "latest_raw_path": "",
                "latest_analysis_id": "",
            },
            "status_distribution": {"raw": 0, "reviewed": 0, "archived": 0},
            "latest_results": [],
            "quick_links": [],
        }
    return repository.get_admin_overview()


@router.get("/admin/classrooms", tags=["Admin API"])
def admin_classrooms(
    q: Optional[str] = None,
    teacher_id: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    from ..main import repository

    if not hasattr(repository, "get_admin_classrooms"):
        return {"success": True, "overview": {}, "items": [], "total": 0}
    return repository.get_admin_classrooms(q=q, teacher_id=teacher_id, limit=limit, offset=offset)


@router.get("/admin/teachers", tags=["Admin API"])
def admin_teachers(
    q: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    from ..main import repository

    if not hasattr(repository, "get_admin_teachers"):
        return {"success": True, "overview": {}, "items": [], "total": 0}
    return repository.get_admin_teachers(q=q, limit=limit, offset=offset)


@router.get("/admin/results", tags=["Admin API"])
def admin_results(
    classroom_id: Optional[str] = None,
    teacher_id: Optional[str] = None,
    status: Optional[str] = None,
    days: Optional[str] = Query(default="30"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    from ..main import repository

    if status not in (None, "", "raw", "reviewed", "archived"):
        raise HTTPException(status_code=400, detail="status must be raw, reviewed, or archived")
    parsed_days = _parse_days(days)
    if not hasattr(repository, "get_admin_results"):
        return {
            "success": True,
            "filters": {
                "classroom_id": classroom_id or "",
                "teacher_id": teacher_id or "",
                "status": status or "",
                "days": parsed_days,
                "limit": limit,
                "offset": offset,
            },
            "overview": {},
            "items": [],
            "total": 0,
        }
    return repository.get_admin_results(
        classroom_id=classroom_id,
        teacher_id=teacher_id,
        status=status,
        days=parsed_days,
        limit=limit,
        offset=offset,
    )


@router.get("/admin/ingestion", tags=["Admin API"])
def admin_ingestion(
    classroom_id: Optional[str] = None,
    device_id: Optional[str] = None,
    source_host: Optional[str] = None,
    days: Optional[str] = Query(default="30"),
    limit: int = Query(default=20, ge=1, le=100),
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    from ..main import repository

    parsed_days = _parse_days(days)
    if not hasattr(repository, "get_admin_ingestion"):
        return {
            "success": True,
            "filters": {
                "classroom_id": classroom_id or "",
                "device_id": device_id or "",
                "source_host": source_host or "",
                "days": parsed_days,
                "limit": limit,
            },
            "overview": {},
            "pipeline": [],
            "devices": [],
            "recent_ingestions": [],
            "video_summary": {"playable": 0, "pending": 0, "missing": 0, "unknown": 0},
            "validation_hints": [],
        }
    return repository.get_admin_ingestion(
        classroom_id=classroom_id,
        device_id=device_id,
        source_host=source_host,
        days=parsed_days,
        limit=limit,
    )


@router.get("/admin/trends", tags=["Admin API"])
def admin_trends(
    classroom_id: Optional[str] = None,
    teacher_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    data_source: str = Query(default="real"),
    limit: int = Query(default=30, ge=1, le=100),
    _: Dict[str, Any] = Depends(_require_admin),
) -> Dict[str, Any]:
    from ..main import repository

    if not hasattr(repository, "get_phase3_admin_trends"):
        return {"success": True, "filters": {"data_source": data_source or "real"}, "overview": {}, "classroom_rankings": [], "teacher_activity": [], "risk_lessons": [], "recent_reports": [], "data_quality": {}}
    return repository.get_phase3_admin_trends(
        classroom_id=classroom_id,
        teacher_id=teacher_id,
        date_from=date_from,
        date_to=date_to,
        data_source=data_source,
        limit=limit,
    )


@router.get("/teacher/results/{result_id}", tags=["Teacher API"])
def teacher_result_detail(result_id: str, current_user: Dict[str, Any] = Depends(_require_teacher)) -> Dict[str, Any]:
    from ..main import repository

    if not hasattr(repository, "get_workbench_result_detail"):
        raise HTTPException(status_code=404, detail="result not found")
    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    result = repository.get_workbench_result_detail(result_id, user_id=user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return {"success": True, "result": result}


@router.patch("/teacher/results/{result_id}/status", tags=["Teacher API"])
def teacher_result_status(
    result_id: str,
    request: StatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(_require_teacher),
) -> Dict[str, Any]:
    from ..main import repository

    if request.status not in {"raw", "reviewed", "archived"}:
        raise HTTPException(status_code=400, detail="status must be raw, reviewed, or archived")
    if not hasattr(repository, "update_workbench_status"):
        raise HTTPException(status_code=404, detail="result not found")
    user_id = current_user["user_id"] if current_user.get("role") == "teacher" else None
    result = repository.update_workbench_status(result_id, request.status, user_id=user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="result not found")
    return {"success": True, "result": result}


@pages_router.get("/health", tags=["System"])
async def health() -> Dict[str, str]:
    """健康检查接口。"""
    return {"status": "ok"}


def _login_redirect() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


@pages_router.get("/", tags=["Pages"])
async def root(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    user = optional_page_user(auth_token)
    if not user:
        return _login_redirect()
    return RedirectResponse(url="/admin" if user.get("role") == "admin" else "/teacher", status_code=302)


@pages_router.get("/login", response_class=HTMLResponse, tags=["Pages"])
async def login_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    user = optional_page_user(auth_token)
    if user:
        return RedirectResponse(url="/admin" if user.get("role") == "admin" else "/teacher", status_code=302)
    return HTMLResponse(content=build_login_html())


@pages_router.get("/register", response_class=HTMLResponse, tags=["Pages"])
async def register_page(auth_token: Optional[str] = Cookie(default=None, alias=AUTH_COOKIE_NAME)):
    user = optional_page_user(auth_token)
    if user:
        return RedirectResponse(url="/admin" if user.get("role") == "admin" else "/teacher", status_code=302)
    return HTMLResponse(content=build_register_html())

