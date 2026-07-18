from rest_framework import serializers
from conversation.models import Participant, Conversation, ConversationType
from accounts.api.v1.serializers import UserSerializer
from accounts.models import Profile



class ParticipantSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(read_only = True, source='user')

    class Meta:
        model = Participant
        fields = ["id", "user_info", "is_conversation_admin", "joined_at"]


class ConversationSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField(read_only=True)
    participants = serializers.SerializerMethodField(read_only=True)

    display_name = serializers.SerializerMethodField(read_only=True)
    display_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "type", "created_by", "name", "created_at", "creator", "participants", "display_name", "display_image"]

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

    def _get_other_participant(self, obj):
        request = self.context.get("request")

        return (
            obj.participants.exclude(user= request.user).first()
        )

    def get_display_name(self, obj):
        if obj.type == ConversationType.GROUP:
            return obj.name

        participant = self._get_other_participant(obj)

        if participant is None:
            return obj.name or "Unknown Conversation"

        user = participant.user

        if hasattr(user, "profile") and user.profile.full_name:
            return user.profile.full_name

        return user.username

    def get_display_image(self, obj):
        if obj.type == ConversationType.GROUP:
            return None
        participant = self._get_other_participant(obj)

        if participant is None:
            return None

        user = participant.user

        if hasattr(user, "profile") and user.profile.profile_pic:
            return user.profile.profile_pic.url

        return None



