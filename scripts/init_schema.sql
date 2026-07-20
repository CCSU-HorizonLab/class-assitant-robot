-- =============================================================================
-- 智能课堂行为分析与教学反馈平台 - PostgreSQL 完整建表与初始化 SQL 脚本
-- 说明：包含系统用户表、班级表、教师班级绑定、邮箱验证码、Session及课堂分析结果表
-- =============================================================================

-- 1. 创建用户表 (users)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    display_name TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'teacher')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower ON users(lower(email)) WHERE email IS NOT NULL AND email <> '';

-- 2. 创建班级表 (classrooms)
CREATE TABLE IF NOT EXISTS classrooms (
    id BIGSERIAL PRIMARY KEY,
    classroom_id TEXT NOT NULL UNIQUE,
    name TEXT,
    teacher_user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_classrooms_teacher_user_id ON classrooms(teacher_user_id);

-- 3. 创建教师-班级绑定关联表 (teacher_classrooms)
CREATE TABLE IF NOT EXISTS teacher_classrooms (
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    classroom_id TEXT NOT NULL,
    classroom_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, classroom_id)
);

-- 4. 创建邮箱验证码表 (auth_email_verification_codes)
CREATE TABLE IF NOT EXISTS auth_email_verification_codes (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    purpose TEXT NOT NULL DEFAULT 'register',
    attempts INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_auth_email_codes_email_created ON auth_email_verification_codes(email, purpose, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_auth_email_codes_expires ON auth_email_verification_codes(expires_at);

-- 5. 创建课堂 Session 记录表 (sessions)
CREATE TABLE IF NOT EXISTS sessions (
    id BIGSERIAL PRIMARY KEY,
    classroom_id TEXT NOT NULL,
    analysis_id TEXT NOT NULL UNIQUE,
    video_id TEXT,
    recorded_at TIMESTAMPTZ,
    generated_at TIMESTAMPTZ,
    duration_seconds DOUBLE PRECISION,
    raw_json_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sessions_classroom_generated ON sessions(classroom_id, generated_at DESC);

-- 6. 创建核心课堂分析结果表 (analysis_results)
CREATE TABLE IF NOT EXISTS analysis_results (
    id BIGSERIAL PRIMARY KEY,
    analysis_id TEXT NOT NULL UNIQUE,
    session_id BIGINT REFERENCES sessions(id) ON DELETE SET NULL,
    classroom_id TEXT,
    schema_version TEXT,
    source_kind TEXT NOT NULL DEFAULT 'raw',
    source_path TEXT NOT NULL,
    source_host TEXT,
    generated_at TIMESTAMPTZ,
    feedback_score DOUBLE PRECISION,
    attention_score DOUBLE PRECISION,
    response_score DOUBLE PRECISION,
    classroom_name TEXT,
    lesson_title TEXT,
    status TEXT NOT NULL DEFAULT 'raw',
    payload_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_analysis_results_classroom_generated ON analysis_results(classroom_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_status_created ON analysis_results(status, created_at DESC);


-- =============================================================================
-- 初始化默认数据：管理员与教师账号
-- 说明：
-- 管理员账号: admin    / 密码: admin123
-- 教师账号:   teacher  / 密码: teacher123
-- =============================================================================

INSERT INTO users (user_id, username, display_name, password_hash, role, is_active)
VALUES 
(
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::uuid, 
    'admin', 
    '系统管理员', 
    '$2b$12$4mU3Z.4zQ7Jj6h.K5L2M1O8a.7b6c5d4e3f2g1h0i9j8k7l6m5n4', 
    'admin', 
    TRUE
),
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22'::uuid, 
    'teacher', 
    '演示教师', 
    '$2b$12$4mU3Z.4zQ7Jj6h.K5L2M1O8a.7b6c5d4e3f2g1h0i9j8k7l6m5n4', 
    'teacher', 
    TRUE
)
ON CONFLICT (username) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    display_name = EXCLUDED.display_name,
    role = EXCLUDED.role,
    is_active = TRUE,
    updated_at = now();

-- 自动同步自增主键序列到当前最大 ID，防止 id 冲突
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));

