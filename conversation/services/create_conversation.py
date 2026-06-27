from rest_framework.exceptions import ValidationError
from django.db.models import Count, Model

import conversation
from conversation.models import Conversation, ConversationType, Participant,MessageType, Message
from django.contrib.auth import get_user_model


User = get_user_model()

class CreateConversation:
    @staticmethod
    def get_direct_key(user1_id, user2_id):
        return f"direct_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

    @staticmethod
    def direct_conversation(request):
        participant_id = request.data.get("participant_id")

        if not participant_id:
            raise ValidationError("Participant_id is required")

        if int(participant_id) == request.user.id:
            raise ValidationError("You cannot chat with yourself.")

        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            raise ValidationError("Participant_id is invalid")

        #CREATE UNIQUE KEY
        key = CreateConversation.get_direct_key(
            request.user.id,
            participant.id
        )

        # GET OR CREATE CONVERSATION
        conversation, created = Conversation.objects.get_or_create(
            type=ConversationType.DIRECT,
            unique_key=key,
            defaults={
                "created_by": request.user
            }
        )

        #Only create participants if new conversation
        if created:
            Participant.objects.bulk_create([
                Participant(
                    conversation=conversation,
                    user=request.user,
                    is_conversation_admin=True
                ),
                Participant(
                    conversation=conversation,
                    user=participant
                )
            ])

        return conversation

    @staticmethod
    def group_conversation(request):
        name = request.data.get("name")
        participants_ids = list(set(request.data.get("participant_ids",[])))

        if request.user.id not in participants_ids:
            participants_ids.append(request.user.id)

        users = User.objects.filter(id__in=participants_ids)
        if len(users) != len(participants_ids):
            raise ValidationError("One or more participant_ids are invalid")

        conversation = Conversation.objects.create(
            name = name,
            type = ConversationType.GROUP,
            created_by = request.user
        )

        participants = [
            Participant(
                conversation=conversation,
                user=user,
                is_conversation_admin=(user.id == request.user.id)
            )
            for user in users
        ]

        Participant.objects.bulk_create(participants)
        return conversation

