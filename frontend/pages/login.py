"""Backward Compatibility Wrapper cho LoginView.

PT Connect - Forwarding to modules.login_view.
"""

from modules.login_view import LoginView


def render_login_page():
    """Wrapper gọi LoginView().render()."""
    LoginView().render()


def is_valid_email(email: str) -> bool:
    """Wrapper gọi LoginView.is_valid_email(email)."""
    return LoginView.is_valid_email(email)
