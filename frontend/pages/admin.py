"""Backward Compatibility Wrapper cho AdminDashboardView.

PT Connect - Forwarding to modules.admin_dashboard_view.
"""

from typing import Any, Dict
from modules.admin_dashboard_view import AdminDashboardView


def render_admin_page(user: Dict[str, Any]):
    """Wrapper gọi AdminDashboardView(user).render()."""
    AdminDashboardView(user).render()
