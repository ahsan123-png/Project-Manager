from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Service
from .serializers import ServiceSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

class ServiceCRUDView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                            name='service_id',
                            type=int,
                            required=False,
                            description="Service ID for specific service retrieval.")
                             ],
                            responses={200: ServiceSerializer(many=True)}
                            )
    def get(self, request):
        service_id = request.query_params.get('service_id')
        queryset = Service.objects.select_related('project')

        if service_id:
            service = get_object_or_404(queryset, id=service_id)
            serializer = ServiceSerializer(service)
            return Response(serializer.data)
        
        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)
    @extend_schema(
        request=ServiceSerializer,
        responses={201: ServiceSerializer}
    )
    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
            request=ServiceSerializer,
        parameters=[
            OpenApiParameter(
                            name='service_id',
                            type=int,
                            required=False,
                            description="Service ID for specific service retrieval.")
                             ],
                            responses={200: ServiceSerializer(many=True)}
                            )
    def patch(self, request):
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response({"error": "ID parameter is required for update."}, status=status.HTTP_400_BAD_REQUEST)

        service = get_object_or_404(Service, id=service_id)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        parameters=[
            OpenApiParameter(
                            name='service_id',
                            type=int,
                            required=False,
                            description="Service ID for specific service retrieval.")
                             ],
                            responses={200: ServiceSerializer(many=True)}
                            )
    def delete(self, request):
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response({"error": "ID parameter is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        service = get_object_or_404(Service, id=service_id)
        service.delete()
        return Response({"message": "Service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
