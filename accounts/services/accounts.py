from django.dispatch import receiver
from django.db.models import Q
from accounts.models import Connection
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
User = get_user_model()

class ConnectionServices:

    @staticmethod
    def get_pending_receive_connections(user):
        connections = Connection.objects.filter(receiver=user, type="pending").order_by("-created_at")
        return connections

    @staticmethod
    def get_sent_connections(user):
        connections = Connection.objects.filter(sender=user, type="pending").order_by("-created_at")
        return connections

    @staticmethod
    def all_connections(user):
        return Connection.objects.filter(
            Q(sender=user) | Q(receiver=user),
            type="accepted"
        ).order_by("-created_at")

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

    @staticmethod
    def update_connection(pk, user, type):
        connection = get_object_or_404(
            Connection,
            id=pk,
            type="pending",
            receiver=user
        )
        connection.type = type
        connection.save()
        return {
            "id": connection.id,
            "sender": connection.sender.id,
            "receiver": connection.receiver.id,
            "status": connection.type
        }



