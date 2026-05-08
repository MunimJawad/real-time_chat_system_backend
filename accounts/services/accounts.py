from rest_framework.response import Response
from rest_framework import status
from accounts.models import Profile, Connection
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
User = get_user_model()

class ConnectionServices:

    @staticmethod
    def create_connection(sender, receiver_id, **kwargs):
       receiver = get_object_or_404(User, pk=int(receiver_id))

       if sender == receiver:
           raise ValueError("You cannot connect with yourself")

       existing = Connection.objects.filter(
           sender=sender,
           receiver=receiver,
       )

       reverse = Connection.objects.filter(
           sender=receiver,
           receiver=sender
       )

       if existing.exists() or reverse.exists():
           raise ValueError("You are already connected")

       connection = Connection.objects.create(
           sender=sender,
           receiver=receiver,
           type="pending"
       )



       return {
           "id": connection.id,
           "sender": sender.id,
           "receiver": receiver.id,
           "status": connection.type
       }

