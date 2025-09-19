from typing import Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import HttpRequest
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from audit.models import AuditLog
from authentication.model_serializers.auth_password_serializers import (
    ForgotPasswordSerializer,
    VerifyResetTokenSerializer,
    ResetPasswordSerializer,
)
from authentication.model_serializers.auth_serializers import LoginSerializer, SignupSerializer
from core.api_views import BaseCreateAPIView
from core.utils import success_response, error_response

from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


def _client_ip(request: HttpRequest) -> Optional[str]:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _build_reset_url(request: HttpRequest, uidb64: str, token: str) -> str:
    base = getattr(settings, "FRONTEND_RESET_PASSWORD_URL", None)
    if base:
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}uidb64={uidb64}&token={token}"
    return request.build_absolute_uri(f"/reset-password?uidb64={uidb64}&token={token}")


def _queue_password_reset_notification(user: AbstractBaseUser, reset_url: str) -> Notification:
    return Notification.objects.create(
        user=user,
        kind=Notification.Kind.SYSTEM,
        channel=Notification.Channel.EMAIL,
        subject="Password reset",
        body=f"Use this link to reset your password: {reset_url}",
        payload={"reset_url": reset_url},
    )


def _send_password_reset_email_immediately(user: AbstractBaseUser, reset_url: str) -> None:
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if not from_email:
        return
    try:
        send_mail(
            "Password reset",
            f"Hello,\n\nUse this link to reset your password:\n{reset_url}\n\nIf you didn't request this, ignore this email.",
            from_email,
            [getattr(user, "email", "")],
            fail_silently=True,
        )
    except Exception:
        pass


class SignupView(BaseCreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        raw = super().post(request, *args, **kwargs)
        if raw.status_code == status.HTTP_200_OK:
            # audit login (best-effort)
            try:
                ser = self.get_serializer(data=request.data)
                ser.is_valid(raise_exception=True)
                user: AbstractBaseUser = ser.user
                AuditLog.objects.create(
                    actor=user,
                    action=AuditLog.Action.LOGIN,
                    target_type="User",
                    target_id=str(user.id),
                    ip_address=_client_ip(request._request),
                    metadata={},
                )
            except Exception:
                pass
            return success_response(result=raw.data, status=status.HTTP_200_OK)
        return error_response(message="Invalid credentials", status=raw.status_code, errors=[raw.data])


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        resp = super().post(request, *args, **kwargs)
        if 200 <= resp.status_code < 300:
            return success_response(result=resp.data, status=resp.status_code)
        return error_response(message="Token refresh failed", status=resp.status_code, errors=[resp.data])


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        try:
            AuditLog.objects.create(
                actor=request.user,  # type: ignore[arg-type]
                action=AuditLog.Action.LOGOUT,
                target_type="User",
                target_id=str(getattr(request.user, "id", "")),
                ip_address=_client_ip(request._request),
                metadata={},
            )
        except Exception:
            pass
        return success_response(message="Logged out.")


class ForgotPasswordView(APIView):
    """
    Accepts email; if user exists creates a reset token + queues/sends mail.
    Always returns 200 to avoid user enumeration.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Invalid payload",
                errors=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email: str = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return success_response(message="If the email exists, a reset link has been sent.")

        uidb64: str = urlsafe_base64_encode(force_bytes(user.pk))
        token: str = PasswordResetTokenGenerator().make_token(user)
        reset_url: str = _build_reset_url(request._request, uidb64, token)  # uses your helper

        # Queue a notification (optional)
        try:
            Notification.objects.create(
                user=user,
                kind=Notification.Kind.SYSTEM,
                channel=Notification.Channel.EMAIL,
                subject="Password reset",
                body=f"Use this link to reset your password: {reset_url}",
                payload={"reset_url": reset_url},
            )
        except Exception:
            pass

        # Try sending immediately (optional)
        try:
            from django.conf import settings
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
            if from_email:
                send_mail(
                    subject="Password reset",
                    message=f"Hello,\n\nUse this link to reset your password:\n{reset_url}\n\nIf you didn't request this, ignore this email.",
                    from_email=from_email,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
        except Exception:
            pass

        return success_response(message="If the email exists, a reset link has been sent.")


class VerifyResetTokenView(APIView):
    """
    Optional endpoint used by the frontend to pre-validate the link.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = VerifyResetTokenSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(message="Token is valid.")
        return error_response(
            message="Invalid or expired token.",
            errors=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResetPasswordView(APIView):
    """
    Accepts uidb64, token, new_password; resets the password if valid.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(message="Password has been reset.")
        return error_response(
            message="Could not reset password.",
            errors=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
