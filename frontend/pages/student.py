"""Backward Compatibility Wrapper cho StudentHomeView.

PT Connect - Forwarding to modules.student_home_view.
"""

from typing import Any, Dict
from modules.student_home_view import StudentHomeView


def render_student_page(user: Dict[str, Any]):
    """Wrapper gọi StudentHomeView(user).render()."""
    StudentHomeView(user).render()
