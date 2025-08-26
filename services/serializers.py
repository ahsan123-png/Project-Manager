from rest_framework import serializers
from .models import Service, ServiceType

class ServiceSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=ServiceType.choices())

    class Meta:
        model = Service
        fields = '__all__'
