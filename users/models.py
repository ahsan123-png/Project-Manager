from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from enum import Enum

# users/models.py
class UserRole(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

    @classmethod
    def values(cls):
        return [item.value for item in cls]

class UserEx(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)  # Explicitly defining email
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices(),
        default=UserRole.EMPLOYEE.value,
        db_index=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"], name="user_email_idx"),
            models.Index(fields=["role"], name="user_role_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.role})"