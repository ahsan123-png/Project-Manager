from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Milestone, MilestoneStatus, Task, TaskStatus
from .serializers import MilestoneSerializer, TaskSerializer
from users.models import UserRole


class TaskCRUDView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Optimized base queryset with select_related and prefetch_related"""
        return Task.objects.select_related(
            'project', 
            'assigned_to',
            'milestone'
        ).only(
            'title',
            'status',
            'deadline',
            'project__name',
            'assigned_to__name',
            'milestone__name'
        )

    def get_filtered_queryset(self, request):
        """Apply filters based on user role and request parameters"""
        queryset = self.get_queryset()
        
        # Employees can only see their own tasks
        if request.user.role == UserRole.EMPLOYEE.value:
            queryset = queryset.filter(assigned_to=request.user)
        
        # Managers can see all tasks in their projects
        elif request.user.role == UserRole.MANAGER.value:
            queryset = queryset.filter(project__manager=request.user)

        # Apply additional filters
        params = request.query_params
        if params.get('task_id'):
            queryset = queryset.filter(id=params['task_id'])
        if params.get('status'):
            queryset = queryset.filter(status=params['status'])
        if params.get('project_id'):
            queryset = queryset.filter(project_id=params['project_id'])
        
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='task_id',
                type=int,
                required=False,
                description="Task ID for specific task retrieval."
            ),
            OpenApiParameter(
                name='status',
                type=str,
                required=False,
                description="Filter tasks by status."
            ),
            OpenApiParameter(
                name='project_id',
                type=int,
                required=False,
                description="Filter tasks by project ID."
            ),
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request):
        queryset = self.get_filtered_queryset(request)
        
        if request.query_params.get('task_id'):
            task = get_object_or_404(queryset)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        if request.user.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can create tasks."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = TaskSerializer(
            data=request.data,
            context={'request': request}  # Pass request for validation
        )
        
        if serializer.is_valid():
            # Automatically set project manager if not provided
            if 'project' in serializer.validated_data:
                project = serializer.validated_data['project']
                if project.manager != request.user:
                    return Response(
                        {"error": "You can only create tasks for your projects."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
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
                description="Task ID for specific task update."
            )
        ],
        responses={200: TaskSerializer}
    )
    def patch(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {"error": "task_id parameter is required for update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = get_object_or_404(self.get_queryset(), id=task_id)
        
        # Permission checks
        if request.user.role == UserRole.EMPLOYEE.value:
            if task.assigned_to != request.user:
                return Response(
                    {"error": "You can only update tasks assigned to you."},
                    status=status.HTTP_403_FORBIDDEN
                )
            # Filter allowed fields for employees
            allowed_fields = {'status', 'notes'}
            if not allowed_fields.issuperset(request.data.keys()):
                return Response(
                    {"error": "Employees can only update status and notes."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        elif request.user.role == UserRole.MANAGER.value:
            if task.project.manager != request.user:
                return Response(
                    {"error": "You can only update tasks in your projects."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = TaskSerializer(
            task, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
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
                description="Task ID for specific task deletion."
            )
        ],
        responses={204: None}
    )
    def delete(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response(
                {"error": "task_id parameter is required for deletion."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = get_object_or_404(self.get_queryset(), id=task_id)
        
        # Permission checks
        if request.user.role == UserRole.EMPLOYEE.value:
            if task.assigned_to != request.user:
                return Response(
                    {"error": "You can only delete tasks assigned to you."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        elif request.user.role == UserRole.MANAGER.value:
            if task.project.manager != request.user:
                return Response(
                    {"error": "You can only delete tasks from your projects."},
                    status=status.HTTP_403_FORBIDDEN
                )

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# ========== Milestone CRUD View ==========
extend_schema(tags=['Milestone'])
class MilestoneView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Milestone.objects.select_related('project', 'project__manager')
        if self.request.user.role == UserRole.MANAGER.value:
            queryset = queryset.filter(project__manager=self.request.user)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='milestone_id',
                type=int,
                required=False,
                description="Milestone ID for specific milestone retrieval."
            ),
            OpenApiParameter(
                name='project_id',
                type=int,
                required=False,
                description="Filter milestones by project ID."
            ),
            OpenApiParameter(
                name='status',
                type=str,
                required=False,
                description="Filter milestones by status.",
                enum=[status.value for status in MilestoneStatus]
            )
        ],
        responses={200: MilestoneSerializer(many=True)}
    )
    def get(self, request):
        milestone_id = request.query_params.get('milestone_id')
        project_id = request.query_params.get('project_id')
        status_filter = request.query_params.get('status')

        queryset = self.get_queryset()
        
        if milestone_id:
            milestone = get_object_or_404(queryset, id=milestone_id)
            serializer = MilestoneSerializer(milestone)
            return Response(serializer.data)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = MilestoneSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=MilestoneSerializer,
        responses={201: MilestoneSerializer}
    )
    def post(self, request):
        if request.user.role != UserRole.MANAGER.value:
            return Response(
                {"error": "Only managers can create milestones."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = MilestoneSerializer(data=request.data)
        if serializer.is_valid():
            # Verify the requesting manager owns the project
            project = serializer.validated_data['project']
            if project.manager != request.user:
                return Response(
                    {"error": "You can only create milestones for projects you manage."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=MilestoneSerializer,
        parameters=[
            OpenApiParameter(
                name='milestone_id',
                type=int,
                required=True,
                description="Milestone ID to update."
            )
        ],
        responses={200: MilestoneSerializer}
    )
    def patch(self, request):
        milestone_id = request.query_params.get('milestone_id')
        if not milestone_id:
            return Response(
                {"error": "milestone_id parameter is required for update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        milestone = get_object_or_404(self.get_queryset(), id=milestone_id)
        
        # Verify the requesting manager owns the project
        if milestone.project.manager != request.user:
            return Response(
                {"error": "You can only update milestones for projects you manage."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = MilestoneSerializer(milestone, data=request.data, partial=True)
        if serializer.is_valid():
            # Prevent changing project ownership
            if 'project' in serializer.validated_data:
                if serializer.validated_data['project'] != milestone.project:
                    return Response(
                        {"error": "Cannot change project association."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='milestone_id',
                type=int,
                required=True,
                description="Milestone ID to delete."
            )
        ],
        responses={204: None}
    )
    def delete(self, request):
        milestone_id = request.query_params.get('milestone_id')
        if not milestone_id:
            return Response(
                {"error": "milestone_id parameter is required for deletion."},
                status=status.HTTP_400_BAD_REQUEST
            )

        milestone = get_object_or_404(self.get_queryset(), id=milestone_id)
        
        # Verify the requesting manager owns the project
        if milestone.project.manager != request.user:
            return Response(
                {"error": "You can only delete milestones for projects you manage."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        milestone.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)