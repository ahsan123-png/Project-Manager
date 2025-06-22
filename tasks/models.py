from django.db import models
from enum import Enum
from django.core.exceptions import ValidationError
from users.models import UserRole
#========= Milstone Model ==========
# models.py
class MilestoneStatus(Enum):
    PLANNING = 'planning'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    DELAYED = 'delayed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Milestone(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(db_index=True)
    milestone_status = models.CharField(
        max_length=20,
        choices=MilestoneStatus.choices(),
        default=MilestoneStatus.PLANNING.value,
        db_index=True
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['milestone_status'], name='milestone_status_idx'),
            models.Index(fields=['deadline'], name='milestone_deadline_idx'),
        ]
        ordering = ['deadline']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name'],
                name='unique_project_milestone'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.project.name})"

    @property
    def manager(self):
        """Derived manager from the associated project"""
        return self.project.manager
    
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
    task_status = models.CharField(
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
    milestone = models.ForeignKey(
        'Milestone',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    deadline = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            # Combined index for status and deadline
            models.Index(fields=['task_status', 'deadline'], name='task_status_deadline_idx'),
            # Single column indexes only where needed
            models.Index(fields=['assigned_to'], name='task_assigned_to_idx'),
        ]
        ordering = ['deadline']

    def clean(self):
        """Validate that milestone belongs to the same project"""
        if self.milestone and self.milestone.project != self.project:
            raise ValidationError(
                "Milestone must belong to the same project as the task"
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation on save
        super().save(*args, **kwargs)

