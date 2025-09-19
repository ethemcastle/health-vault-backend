from typing import Any, Dict
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

User = get_user_model()
token_gen = PasswordResetTokenGenerator()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value


class VerifyResetTokenSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        try:
            uid: str = force_str(urlsafe_base64_decode(attrs["uidb64"]))
            user: AbstractBaseUser = User.objects.get(pk=uid)
        except Exception as exc:
            raise serializers.ValidationError("Invalid link.") from exc
        if not token_gen.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Invalid or expired token.")
        attrs["user"] = user
        return attrs


class ResetPasswordSerializer(VerifyResetTokenSerializer):
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value: str) -> str:
        password_validation.validate_password(value)
        return value

    def save(self, **kwargs: Any) -> AbstractBaseUser:
        user: AbstractBaseUser = self.validated_data["user"]
        new_password: str = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
