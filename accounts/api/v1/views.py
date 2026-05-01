from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.api.v1.serializers import RegisterSerializer, LoginSerializer 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from accounts.throttles import LoginThrottle, RegisterThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError

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
            "user": {
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


