from django.urls import path

from authentication.model_views.auth_view import (
    SignupView, LoginView, RefreshView, LogoutView,
    ForgotPasswordView, VerifyResetTokenView, ResetPasswordView,
)
from authentication.model_views.user_view import (
    UserListCreateView, UserRUDView,
)

app_name = "authentication"

urlpatterns = [
    # Auth
    path("signup/", SignupView.as_view(), name="auth-signup"),
    path("knock/knock/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),

    # Password reset flow
    path("forgot-password/", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("verify-reset-token/", VerifyResetTokenView.as_view(), name="auth-verify-reset-token"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),

    # Users (admin-managed)
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserRUDView.as_view(), name="user-rud"),
]
