from rest_framework import serializers
from conversation.models import Participant
from accounts.api.v1.serializers import UserSerializer

class ParticipantSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(read_only = True, source='user')

    class Meta:
        model = Participant
        fields = ["id", "user_info", "is_conversation_admin", "joined_at"]