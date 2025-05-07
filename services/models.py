from django.db import models
from enum import Enum

class ServiceType(Enum):
    DOMAIN = 'domain'
    HOSTING = 'hosting'
    SERVER = 'server'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Service(models.Model):
    type = models.CharField(
        max_length=20,
        choices=ServiceType.choices(),
        db_index=True
    )
    details = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(db_index=True)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='services'
    )

    class Meta:
        indexes = [
            models.Index(fields=['type'], name='service_type_idx'),
            models.Index(fields=['end_date'], name='service_end_date_idx'),
        ]