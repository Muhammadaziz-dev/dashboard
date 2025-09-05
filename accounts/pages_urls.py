from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import DashboardView, DashboardStateView, DashboardSaveView, DashboardClearView, LessonAddView, LessonRemoveView

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
]
