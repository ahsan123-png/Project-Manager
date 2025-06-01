from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Notification

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Unread Notification Example',
            value={
                'id': 1,
                'message': 'Project "Website Redesign" deadline in 2 days',
                'related_type': 'project',
                'related_id': 5,
                'is_read': False,
                'created_at': '2023-06-15T09:30:00Z'
            },
            response_only=True
        )
    ]
)
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'related_type', 'related_id', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        """Optimized representation with cached data"""
        data = super().to_representation(instance)
        data['related_object'] = self._get_related_object(instance)
        return data

    def _get_related_object(self, instance):
        """Lazy-load related object details"""
        from django.contrib.contenttypes.models import ContentType
        try:
            model_class = ContentType.objects.get(model=instance.related_type).model_class()
            return model_class.objects.filter(pk=instance.related_id).values('name', 'status').first()
        except Exception:
            return None