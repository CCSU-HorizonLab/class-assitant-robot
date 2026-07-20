"""Login and permission pages for Phase 3.1 polished UI, migrated to Jinja2."""
from __future__ import annotations

from cloud_backend.utils.templates import render_template


def build_login_html() -> str:
    """Render the login page using Jinja2."""
    return render_template("login.html")


def build_register_html() -> str:
    """Render the registration page using Jinja2."""
    return render_template("register.html")


def build_forbidden_html() -> str:
    """Render the forbidden/permission error page using Jinja2."""
    return render_template("forbidden.html")
