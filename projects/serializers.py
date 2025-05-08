# serializers.py

from rest_framework import serializers
from .models import Client, Project, ProjectStatus

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ProjectStatus.choices()) 

