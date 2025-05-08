from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404
from .models import Project , Client
from .serializers import ClientSerializer
from .serializers import ProjectSerializer, ProjectStatusSerializer
# =========== views.py ===========
class ClientView(APIView):
    @extend_schema(responses={200: ClientSerializer(many=True)})
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    @extend_schema(request=ClientSerializer, responses={201: ClientSerializer})
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetailView(APIView):
    @extend_schema(responses={200: ClientSerializer})
    def get(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=404)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    @extend_schema(request=ClientSerializer, responses={200: ClientSerializer})
    def patch(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=404)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=404)
        client.delete()
        return Response(status=204)


class ProjectView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', description='Project ID to retrieve a single record', required=False, type=int),
        ],
        responses={200: ProjectSerializer(many=True)},
    )
    def get(self, request):
        project_id = request.query_params.get('id')
        if project_id:
            project = get_object_or_404(Project.objects.select_related('client'), pk=project_id)
            serializer = ProjectSerializer(project)
            return Response(serializer.data)
        projects = Project.objects.select_related('client').all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @extend_schema(request=ProjectSerializer, responses={201: ProjectSerializer})
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(
        request=ProjectStatusSerializer,
        parameters=[
            OpenApiParameter(name='id', description='Project ID to update status', required=True, type=int),
        ],
        responses={200: ProjectSerializer},
        description="Update only the status of a project using ?id=<project_id>"
    )
    def patch(self, request):
        project_id = request.query_params.get('id')
        if not project_id:
            return Response({'error': 'Missing project ID in query parameters'}, status=400)
        
        project = get_object_or_404(Project.objects.select_related('client'), pk=project_id)

        status_serializer = ProjectStatusSerializer(data=request.data)
        if status_serializer.is_valid():
            project.status = status_serializer.validated_data['status']
            project.save()
            return Response(ProjectSerializer(project).data)
        return Response(status_serializer.errors, status=400)
