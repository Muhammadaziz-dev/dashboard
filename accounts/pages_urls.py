from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    DashboardView,
    DashboardStateView,
    DashboardSaveView,
    DashboardClearView,
    LessonAddView,
    LessonRemoveView,
    StudentAddView,
    StudentRemoveView,
    DashboardExportView,
)

urlpatterns = [
    path("login/", LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", DashboardView.as_view(), name="dashboard"),
    # Dashboard APIs (session-auth protected)
    path("dashboard/state/", DashboardStateView.as_view(), name="dashboard_state"),
    path("dashboard/save/", DashboardSaveView.as_view(), name="dashboard_save"),
    path("dashboard/clear/", DashboardClearView.as_view(), name="dashboard_clear"),
    path("dashboard/lesson/add/", LessonAddView.as_view(), name="dashboard_lesson_add"),
    path("dashboard/lesson/remove/", LessonRemoveView.as_view(), name="dashboard_lesson_remove"),
    path("dashboard/student/add/", StudentAddView.as_view(), name="dashboard_student_add"),
    path("dashboard/student/remove/", StudentRemoveView.as_view(), name="dashboard_student_remove"),
    path("dashboard/export/", DashboardExportView.as_view(), name="dashboard_export"),
]
