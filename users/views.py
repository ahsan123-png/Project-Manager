from django.shortcuts import render
from users.models import UserEx, UserRole
# Create your views here.
from rest_framework import generics, status
from adrf.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, CustomTokenObtainSerializer, UserProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes,OpenApiExample
import logging
import asyncio
from asgiref.sync import sync_to_async
from rest_framework.generics import GenericAPIView

logger = logging.getLogger(__name__)
@extend_schema(tags=["User"])
class UserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: UserSerializer(many=True)},
        description="List users or filter by ID and role",
        parameters=[
            OpenApiParameter(name='id',
                            type=OpenApiTypes.INT,
                            location=OpenApiParameter.QUERY,
                            required=False,
                            description='Filter by user ID'),

            OpenApiParameter(name='role',
                            type=OpenApiTypes.STR,
                            location=OpenApiParameter.QUERY,
                            required=False,
                            description='Filter users by role',
                            enum=UserRole.values()),
                        ]
                    )
    def get(self, request, *args, **kwargs):
        """List users or retrieve specific user"""
        user_id = request.query_params.get('id')
        role = request.query_params.get('role')
        if user_id:
            try:
                user = UserEx.objects.get(pk=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except UserEx.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        users = UserEx.objects.all()
        if role:
            users = users.filter(role=role)

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer},
        description="Create a new user",
        examples=[OpenApiExample(
            'Example request',
            value={"email": "user@example.com", "password": "securepassword123", "name": "John Doe", "age": 30, "role": "employee"},
            request_only=True
        )]
    )
    def post(self, request, *args, **kwargs):
        """Create user"""
        serializer = UserSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            logger.error(f"Validation error: {serializer.errors}")
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        description="Partially update a user by ID (via query parameter)",
        parameters=[
            OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=True, description='User ID to update'),
        ],
        examples=[OpenApiExample(
            'Example request',
            value={"name": "Updated Name", "age": 31},
            request_only=True
        )]
    )
    def patch(self, request, *args, **kwargs):
        """Partial update via query param"""
        user_id = request.query_params.get('id')
        if not user_id:
            return Response({"error": "ID query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserEx.objects.get(pk=user_id)
        except UserEx.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            logger.error(f"Validation error: {serializer.errors}")
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        description="Delete a user by ID (via query parameter)",
        parameters=[
            OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=True, description='User ID to delete'),
        ]
    )
    def delete(self, request, *args, **kwargs):
        """Delete user via query param"""
        user_id = request.query_params.get('id')
        if not user_id:
            return Response({"error": "ID query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserEx.objects.get(pk=user_id)
        except UserEx.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#==== Login ======   
@extend_schema(tags=["Auth"])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer

    @extend_schema(
        description="Login with email/password to get JWT tokens",
        request=CustomTokenObtainSerializer,
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
#==== Profile ======
@extend_schema(tags=["Auth"])
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        description="Get current user profile",
        responses={200: UserProfileSerializer}
    )
    async def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return Response(
                {"error": "Failed to fetch profile"},
                status=status.HTTP_400_BAD_REQUEST
            )