from rest_framework import serializers
from conversation.models import Participant, Conversation, ConversationType
from accounts.api.v1.serializers import UserSerializer



class ParticipantSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(read_only = True, source='user')

    class Meta:
        model = Participant
        fields = ["id", "user_info", "is_conversation_admin", "joined_at"]


class ConversationSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField(read_only=True)
    participants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "type", "created_by", "name", "created_at", "creator", "participants"]

    def get_creator(self, obj):
        return {
            "id": obj.created_by.id,
            "username": obj.created_by.username,
        }

    def get_participants(self, obj):
        participants = obj.participants.all()
        if obj.type == ConversationType.DIRECT:
            participant = participants.first()
            if participant:
                return ParticipantSerializer(participant).data

            return None

        return ParticipantSerializer(participants, many=True).data
