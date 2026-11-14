"""Module chứa các Lớp Giao diện (Boundary Views) theo mô hình BCE.

PT Connect - Frontend Architecture.
"""

from modules.login_view import LoginView
from modules.student_home_view import StudentHomeView
from modules.pt_home_view import PTHomeView
from modules.admin_dashboard_view import AdminDashboardView

__all__ = [
    "LoginView",
    "StudentHomeView",
    "PTHomeView",
    "AdminDashboardView",
]

