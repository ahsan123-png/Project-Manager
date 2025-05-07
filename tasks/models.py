from django.db import models
from enum import Enum

from users.models import UserRole

class TaskStatus(Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices(),
        default=TaskStatus.NOT_STARTED.value,
        db_index=True
    )
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'users.UserEx',
        on_delete=models.CASCADE,
        limit_choices_to={'role': UserRole.EMPLOYEE.value},
        related_name='tasks'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    deadline = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status'], name='task_status_idx'),
            models.Index(fields=['deadline'], name='task_deadline_idx'),
            models.Index(fields=['assigned_to'], name='task_assigned_to_idx'),
            models.Index(fields=['project'], name='task_project_idx'),
        ]
        ordering = ['deadline']