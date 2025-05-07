from rest_framework import serializers
from .models import UserEx, UserRole
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = UserEx
        fields = '__all__'
        extra_kwargs = {
            'role': {'required': True}
        }
    

    def validate_role(self, value):
        if value not in UserRole.values():
            raise serializers.ValidationError("Invalid role specified")
        return value

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        user = UserEx.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', UserRole.EMPLOYEE.value)
        )
        return user
#== login ======
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Admin Login',
            value={'email': 'admin@example.com', 'password': 'secure123'},
            request_only=True
        )
    ]
)
class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    def validate(self, attrs):
        # Default validation (checks credentials and returns tokens)
        data = super().validate(attrs)
        user = self.user 
        data.update({
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'age': user.age,
        })
        return data
# == user profile ==
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEx
        fields = ['email', 'name', 'age', 'role']