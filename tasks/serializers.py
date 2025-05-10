from rest_framework import serializers
from .models import Task , Milestone

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id', 'project', 'assigned_to', 'deadline', 'title', 'description')

class MilestoneSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_manager(self, obj):
        """Include manager information from the project"""
        return {
            'id': obj.project.manager.id,
            'name': obj.project.manager.name,
            'email': obj.project.manager.email
        }