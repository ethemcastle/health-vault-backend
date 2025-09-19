from typing import Dict

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import AccessToken

from authentication.const import ADMIN, Gender
from core.models import BaseModel


class MyUserManager(BaseUserManager):
    """Email as username; normal login only."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email address must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("first_name", "admin")
        extra_fields.setdefault("last_name", "admin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self._create_user(email, password, **extra_fields)
        try:
            user.group = Group.objects.get(name=ADMIN)
            user.save(update_fields=["group"])
        except Group.DoesNotExist:
            pass
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    class Meta:
        verbose_name = "User"
        db_table = "auth_user"

    email = models.EmailField(unique=True)
    first_name = models.CharField(_("first name"), max_length=50, blank=True, default="")
    last_name = models.CharField(_("last name"), max_length=50, blank=True, default="")

    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, blank=True, null=True)

    group = models.ForeignKey(
        Group,
        related_name="primary_group_users",
        on_delete=models.SET_NULL,  # safer than CASCADE
        null=True,
        blank=True,
    )

    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def is_admin(self) -> bool:
        return bool(self.group and self.group.name == ADMIN)

    @staticmethod
    def get_user_by_token(data: Dict):
        token_user_id = AccessToken(data["token"])["user_id"]
        return User.objects.get(id=token_user_id)
