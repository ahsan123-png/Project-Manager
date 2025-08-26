from django.db import models
from users.models import UserEx
from projects.models import Project
from enum import Enum

class ReportType(Enum):
    PROJECT_PROGRESS = 'project_progress'
    TEAM_PERFORMANCE = 'team_performance'
    DEADLINE_RISK = 'deadline_risk'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]

class Report(models.Model):
    report_type = models.CharField(max_length=20, choices=ReportType.choices())
    generated_by = models.ForeignKey(
        UserEx,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['admin', 'manager']}
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    filters = models.JSONField(default=dict)  # {'timeframe': 'last_week'}
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_cached = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_cached']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()} Report ({self.created_at.date()})"
