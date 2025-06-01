from rest_framework import generics, status
from rest_framework.response import Response
from .models import Report
from .serializers import ReportCreateSerializer, ReportDetailSerializer
from .services import ReportGenerator
from drf_spectacular.utils import extend_schema
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportCreateSerializer

    @extend_schema(
        description="Generate a new report (Admins/Managers only)",
        responses={201: ReportDetailSerializer}
    )
    async def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Check cache first
            cache_key = self._get_cache_key(serializer.validated_data)
            cached_data = await sync_to_async(cache.get)(cache_key)
            
            if cached_data:
                report = await sync_to_async(Report.objects.create)(
                    **serializer.validated_data,
                    generated_by=request.user,
                    data=cached_data,
                    is_cached=True
                )
            else:
                # Generate fresh report
                data = await self._generate_report(serializer.validated_data)
                report = await sync_to_async(Report.objects.create)(
                    **serializer.validated_data,
                    generated_by=request.user,
                    data=data
                )
                # Cache for 1 hour
                await sync_to_async(cache.set)(cache_key, data, 3600)

            return Response(
                ReportDetailSerializer(report).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return Response(
                {"error": "Report generation failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

    async def _generate_report(self, validated_data):
        report_type = validated_data['report_type']
        project = validated_data.get('project')
        filters = validated_data.get('filters', {})

        if report_type == 'project_progress':
            return await ReportGenerator.generate_project_progress(project.id, filters)
        # Add other report types here...

    def _get_cache_key(self, data):
        return f"report_{data['report_type']}_{data.get('project', '')}_{json.dumps(data.get('filters', {}), sort_keys=True)}"