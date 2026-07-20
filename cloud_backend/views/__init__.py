"""Views and HTML templates package."""
from __future__ import annotations

from .style import PHASE31_STYLE, role_label
from .login_templates import build_forbidden_html, build_login_html, build_register_html
from .teacher_templates import build_teacher_home_html, build_teacher_reports_html, build_teacher_results_html
from .admin_templates import (
    build_admin_classrooms_html,
    build_admin_home_html,
    build_admin_ingestion_html,
    build_admin_results_html,
    build_admin_teachers_html,
)
from .dashboard_v11 import build_results_center_html, latest_result_or_404

__all__ = [
    "PHASE31_STYLE",
    "role_label",
    "build_forbidden_html",
    "build_login_html",
    "build_register_html",
    "build_teacher_home_html",
    "build_teacher_reports_html",
    "build_teacher_results_html",
    "build_admin_classrooms_html",
    "build_admin_home_html",
    "build_admin_ingestion_html",
    "build_admin_results_html",
    "build_admin_teachers_html",
    "build_results_center_html",
    "latest_result_or_404",
]
