from django.db import models
from enum import Enum
from users.models import UserEx

class NotificationType(Enum):
    PROJECT = 'project'
    TASK = 'task'
    SERVICE = 'service'
    MILESTONE = 'milestone'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Notification(models.Model):
    user = models.ForeignKey(
        UserEx,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )
    message = models.TextField()
    related_id = models.PositiveIntegerField()  # ID of project/task/service
    related_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices(),
        db_index=True
    )
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read'], name='notif_user_unread_idx'),
            models.Index(fields=['created_at'], name='notif_created_at_idx'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}"