from rest_framework import serializers
from .models import Task , Milestone
from drf_spectacular.utils import extend_schema_field
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        ref_name = 'TaskSerializer'
        # read_only_fields = ('id', 'project', 'assigned_to', 'deadline', 'title', 'description')

class MilestoneSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'name': {'type': 'string'},
            'email': {'type': 'string', 'format': 'email'},
        }
    })
    def get_manager(self, obj) -> dict:
        """Include manager information from the project"""
        return {
            'id': obj.project.manager.id,
            'name': obj.project.manager.name,
            'email': obj.project.manager.email
        }