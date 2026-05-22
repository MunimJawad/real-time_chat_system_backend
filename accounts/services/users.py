from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
User = get_user_model()

class UserService:
    @staticmethod
    def get_users(search):
        if search:
            users = User.objects.filter(Q(username__icontains=search) | Q(email__icontains=search))
        else:
            users = User.objects.all()

        return users
