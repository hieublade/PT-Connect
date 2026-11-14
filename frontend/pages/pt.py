"""Backward Compatibility Wrapper cho PTHomeView.

PT Connect - Forwarding to modules.pt_home_view.
"""

from typing import Any, Dict
from modules.pt_home_view import PTHomeView, confirm_create_slot_dialog


def render_pt_page(user: Dict[str, Any]):
    """Wrapper gọi PTHomeView(user).render()."""
    PTHomeView(user).render()
