from celery import shared_task
from django.utils import timezone
from .models import Notification
from django.db.models import Q
import asyncio

@shared_task
def check_pending_notifications():
    """Batch process notifications for better performance"""
    from django.db import connection
    connection.close()  # Prevent DB connection leaks
    
    async def process():
        # Expire old notifications after 30 days
        await Notification.objects.filter(
            created_at__lte=timezone.now() - timezone.timedelta(days=30)
        ).adelete()
        
        # Mark stale unread notifications
        await Notification.objects.filter(
            is_read=False,
            created_at__lte=timezone.now() - timezone.timedelta(days=7)
        ).aupdate(is_read=True)
    
    asyncio.run(process())