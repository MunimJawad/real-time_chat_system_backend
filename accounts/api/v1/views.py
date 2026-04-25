from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.api.v1.serializers import RegisterSerializer, LoginSerializer 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from accounts.throttles import LoginThrottle, RegisterThrottle

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

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

        return Response({"message": "Logged out"})    
    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
                  
         return Response({
            "message": "You are authenticated",
            "user": {
                  "username": request.user.username,
                  "email": request.user.email
                }
        })

            
class Home(APIView):
    def get(self, request):
      return Response({
          "message": "Hello Munim"
      })

