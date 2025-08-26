from users.models import UserRole  # Assuming UserRole is defined in users/models.py
from django.db import models
from enum import Enum

class ProjectStatus(Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ON_HOLD = 'on_hold'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Client(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20)
    details = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='client_name_idx'),
        ]

class Project(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    deadline = models.DateField(db_index=True)
    project_status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices(),
        default=ProjectStatus.NOT_STARTED.value,
        db_index=True
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    manager = models.ForeignKey(
        'users.UserEx',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': UserRole.MANAGER.value},
        related_name='managed_projects'
    )

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='project_name_idx'),
            models.Index(fields=['deadline'], name='project_deadline_idx'),
            models.Index(fields=['project_status'], name='project_status_idx'),
            models.Index(fields=['manager'], name='project_manager_idx'),
        ]