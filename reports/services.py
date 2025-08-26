from django.db import connection
from asgiref.sync import sync_to_async
from projects.models import Project
from tasks.models import Task
import json
import asyncio
from datetime import timedelta
from django.utils import timezone

class ReportGenerator:
    @staticmethod
    async def generate_project_progress(project_id, filters):
        """Async project progress report with raw SQL"""
        async with connection.cursor() as cursor:
            # Main metrics
            await cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as task_count,
                    AVG(EXTRACT(EPOCH FROM (deadline - created_at))/86400 as avg_duration_days
                FROM tasks_task
                WHERE project_id = %s
                GROUP BY status
            """, [project_id])
            metrics = await ReportGenerator._dictfetchall(cursor)

            # Timeline data
            await cursor.execute("""
                SELECT 
                    DATE(created_at) as day,
                    COUNT(*) as created,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM tasks_task
                WHERE project_id = %s
                GROUP BY DATE(created_at)
                ORDER BY day
            """, [project_id])
            timeline = await ReportGenerator._dictfetchall(cursor)

        return {
            'metrics': metrics,
            'timeline': timeline,
            'summary': await ReportGenerator._project_summary(project_id)
        }

    @staticmethod
    async def _project_summary(project_id):
        project = await sync_to_async(Project.objects.get)(id=project_id)
        overdue = await sync_to_async(Task.objects.filter(
            project_id=project_id,
            deadline__lt=timezone.now(),
            status__in=['not_started', 'in_progress']
        ).count)()
        
        return {
            'project_name': project.name,
            'total_tasks': await sync_to_async(project.tasks.count)(),
            'overdue_tasks': overdue
        }

    @staticmethod
    async def _dictfetchall(cursor):
        """Convert cursor results to dict"""
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) async for row in cursor]