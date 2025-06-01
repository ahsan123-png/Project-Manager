from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Notification
from projects.models import Project, Service
from tasks.models import Task, Milestone
from users.models import User
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

# Admin Notifications
@receiver(post_save, sender=Project)
def notify_admin_project_deadline(sender, instance, created, **kwargs):
    if not created and instance.deadline:
        remaining = (instance.deadline - timezone.now().date()).days
        if remaining == 2:
            Notification.objects.acreate(
                user=instance.manager,
                message=f"Admin Alert: Project '{instance.name}' deadline in 2 days",
                related_id=instance.id,
                related_type='project'
            )

@receiver(post_save, sender=Service)
def notify_service_expiry(sender, instance, created, **kwargs):
    if not created and instance.end_date:
        remaining = (instance.end_date - timezone.now().date()).days
        if remaining <= 3:
            admins = User.objects.filter(role='admin').only('id')
            Notification.objects.abulk_create([
                Notification(
                    user=admin,
                    message=f"Service {instance.get_type_display()} expires in {remaining} days",
                    related_id=instance.id,
                    related_type='service'
                ) for admin in admins
            ])

# Manager Notifications
@receiver(post_save, sender=Project)
def notify_manager_project_assignment(sender, instance, created, **kwargs):
    if created and instance.manager:
        Notification.objects.acreate(
            user=instance.manager,
            message=f"New project assigned: {instance.name}",
            related_id=instance.id,
            related_type='project'
        )

@receiver(post_save, sender=Milestone)
def notify_milestone_deadline(sender, instance, created, **kwargs):
    if not created and instance.deadline:
        remaining = (instance.deadline - timezone.now().date()).days
        if remaining == 1:
            Notification.objects.acreate(
                user=instance.project.manager,
                message=f"Milestone '{instance.name}' deadline tomorrow",
                related_id=instance.id,
                related_type='milestone'
            )

# Employee Notifications
@receiver(post_save, sender=Task)
def handle_task_notifications(sender, instance, created, **kwargs):
    if created:
        # Task assignment
        Notification.objects.acreate(
            user=instance.assigned_to,
            message=f"New task assigned: {instance.title}",
            related_id=instance.id,
            related_type='task'
        )
    elif instance.deadline:
        # Deadline alert
        remaining = (instance.deadline - timezone.now()).days
        if remaining == 1:
            Notification.objects.acreate(
                user=instance.assigned_to,
                message=f"Task '{instance.title}' deadline tomorrow",
                related_id=instance.id,
                related_type='task'
            )