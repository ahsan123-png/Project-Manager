from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer
from drf_spectacular.utils import extend_schema
import logging

logger = logging.getLogger(__name__)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="List all notifications (marks as read on fetch)",
        responses={200: NotificationSerializer(many=True)}
    )
    def get_queryset(self):
        try:
            # Single atomic query for read+update
            with transaction.atomic():
                queryset = Notification.objects.filter(
                    user=self.request.user
                ).select_related('user').order_by('-created_at')
                
                # Efficient mark-as-read
                queryset.filter(is_read=False).update(is_read=True)
                
                return queryset
        except Exception as e:
            logger.error(f"Notification fetch error: {str(e)}")
            return Notification.objects.none()

class NotificationMarkReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Mark notification as read",
        request=None,
        responses={204: None}
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save(update_fields=['is_read'])
        return Response(status=status.HTTP_204_NO_CONTENT)

class UnreadCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Get count of unread notifications",
        responses={200: {"count": int}}
    )
    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})