from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Task, TaskStatus
from .serializers import TaskSerializer
from users.models import UserRole


class TaskCRUDView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='task_id',
                type=int,
                required=False,
                description="Task ID for specific task retrieval."),
            OpenApiParameter(
                name='status',
                type=str,
                required=False,
                description="Filter tasks by status."),
            OpenApiParameter(
                name='porject_id',
                type=int,
                required=False,
                description="Filter tasks by project ID."),
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request):
        task_id = request.query_params.get('task_id')
        status_param = request.query_params.get('status')
        project_id = request.query_params.get('project_id')

        queryset = Task.objects.select_related('project', 'assigned_to')

        if task_id:
            task = get_object_or_404(queryset, id=task_id)
            serializer = TaskSerializer(task)
            return Response(serializer.data)

        if status_param:
            queryset = queryset.filter(status=status_param)

        if project_id:
            queryset = queryset.filter(project__id=project_id)

        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)
    @extend_schema(
        request=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        if request.user.role != UserRole.MANAGER.value:
            return Response({"error": "Only managers can create tasks."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        request=TaskSerializer,
       parameters=[
            OpenApiParameter(
                name='task_id',
                type=int,
                required=True,
                description="Task ID for specific task update.")
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def patch(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({"error": "ID parameter is required for update."}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        # Employees can only update status and notes of tasks assigned to them
        if request.user.role == UserRole.EMPLOYEE.value:
            if task.assigned_to != request.user:
                return Response({"error": "You can only update tasks assigned to you."}, status=status.HTTP_403_FORBIDDEN)
            # Allow only status and notes to be updated
            allowed_fields = ['status', 'notes']
            for field in request.data.keys():
                if field not in allowed_fields:
                    return Response({"error": f"You can only update {', '.join(allowed_fields)}."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='task_id',
                type=int,
                required=True,
                description="Task ID for specific task deletion.")
        ],
        responses={204: None}
    )
    def delete(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({"error": "ID parameter is required for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        # Employees can only delete tasks assigned to them
        if request.user.role == UserRole.EMPLOYEE.value:
            if task.assigned_to != request.user:
                return Response({"error": "You can only delete tasks assigned to you."}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
