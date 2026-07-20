from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from cloud_backend.views.style import PHASE31_STYLE

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True
)

# Bind PHASE31_STYLE as a global variable in Jinja2
jinja_env.globals["PHASE31_STYLE"] = PHASE31_STYLE

def render_template(template_name: str, **context) -> str:
    """Render a Jinja2 template and return the resulting HTML string."""
    template = jinja_env.get_template(template_name)
    return template.render(**context)
