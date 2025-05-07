from django.db import models
from users.models import UserEx, UserRole
from projects.models import Project

class Report(models.Model):
    REPORT_TYPES = [
        ('project_progress', 'Project Progress'),
        ('team_performance', 'Team Performance'),
        ('deadline_risk', 'Deadline Risk'),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(
        UserEx,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': UserRole.values()}
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    data = models.JSONField()  # Stores all report metrics
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['report_type'], name='report_type_idx'),
            models.Index(fields=['created_at'], name='report_created_at_idx'),
        ]