from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Report

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Project Progress Request',
            value={
                "report_type": "project_progress",
                "project": 1,
                "filters": {
                    "timeframe": "last_month",
                    "include_completed": True
                }
            },
            request_only=True
        )
    ]
)
class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['report_type', 'project', 'filters']
        extra_kwargs = {
            'project': {'required': False}
        }

class ReportDetailSerializer(serializers.ModelSerializer):
    generated_by = serializers.StringRelatedField()
    project = serializers.StringRelatedField()

    class Meta:
        model = Report
        fields = '__all__'