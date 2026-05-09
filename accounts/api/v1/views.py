from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.api.v1.serializers import RegisterSerializer, LoginSerializer, ProfileSerializer, ConnectionSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from accounts.throttles import LoginThrottle, RegisterThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from accounts.models import Profile, Connection
from django.contrib.auth import get_user_model
from accounts.services.accounts import ConnectionServices
User = get_user_model()

class RegisterView(APIView):
    throttle_classes = [RegisterThrottle]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        #If user creation is event driven 
        #with transaction.atomic():
        #   serializer.save()
        return Response({
            "message": "User created successfully",
        } , status=status.HTTP_201_CREATED )
    
    
class LoginView(APIView):
    throttle_classes = [LoginThrottle]
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "message": "Login successful",
            "access": str(access_token),
            "refresh": str(refresh),
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid, expired or already blacklisted token"},
                status=status.HTTP_400_BAD_REQUEST
            )

    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


            
class Home(ProtectedView):

    def get(self, request):

      return Response({
          "message": "Hello Munim"
      })


class ProfileView(ProtectedView):
    def get_profile(self, pk):
        return get_object_or_404(Profile, id=pk)

    def get(self, request, profile_id):
        profile = self.get_profile(profile_id)
        serializer = ProfileSerializer(profile)
        return Response({
            "profile": serializer.data,
        },status=status.HTTP_200_OK)

    def put(self, request, profile_id):
        profile = self.get_profile(profile_id)
        if profile.user !=request.user:
            return Response({
                "error": "You are not allowed to do this"
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "profile": serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class ConnectionView(ProtectedView):
    def post(self, request):
        sender = request.user
        receiver_id = request.data.get("receiver")

        connection = ConnectionServices.create_connection(sender, receiver_id)

        return Response({
            "message": "Request sent successfully",
            "data": connection
        }, status=status.HTTP_201_CREATED)


class ConnectionUpdateView(ProtectedView):
    def post(self, request, pk):
        user = request.user
        type = request.data.get("type")
        connection = ConnectionServices.update_connection(pk, user, type)



        return Response(
            {
                "message": "Connection updated successfully",
                "data": connection
            },
            status=status.HTTP_200_OK
        )


class PendingReceivedConnectionsView(ProtectedView):
    def get(self, request):
        user = request.user
        connections = ConnectionServices.get_pending_receive_connections(user)
        serializer = ConnectionSerializer(connections, many=True)
        return Response({
            "message": "Received pending connections",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class PendingSentConnectionsView(ProtectedView):
    def get(self, request):
        user = request.user
        connections = ConnectionServices.get_sent_connections(user)
        serializer = ConnectionSerializer(connections, many=True)
        return Response({
            "message": "Sent pending connections",
            "data": serializer.data
        }, status=status.HTTP_200_OK)