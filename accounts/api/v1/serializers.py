from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from accounts.models import Profile, Connection

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ["id","username","email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email = value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
       return User.objects.create_user(**validated_data)
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username = email, password = password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")
        

        data["user"] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email"]

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = Profile
        fields = ["id", "user", "full_name", "bio", "profile_pic", "cover_pic",
                  "date_of_birth", "workplace", "location", "gender", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.profile_pic = validated_data.get("profile_pic", instance.profile_pic)
        instance.date_of_birth = validated_data.get("date_of_birth", instance.date_of_birth)
        instance.workplace = validated_data.get("workplace", instance.workplace)
        instance.location = validated_data.get("location", instance.location)
        instance.gender = validated_data.get("gender", instance.gender)

        instance.save()
        return instance


class ConnectionSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only = True)
    receiver = UserSerializer(read_only = True)
    class Meta:
        model = Connection
        fields = ["id", "sender", 'receiver', 'type', "created_at"]

class ConnectionSentSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = Connection
        fields = ["id", "sender", 'receiver', 'type', "created_at"]



