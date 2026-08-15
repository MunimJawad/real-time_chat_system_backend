
from conversation.models import Conversation, Participant, ConversationType
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
User = get_user_model()

class ParticipantService:
    @staticmethod
    def add_participants(conversation, user_ids):

        if conversation.type != ConversationType.GROUP:
            raise ValidationError(
                "Participants can only be added to group conversations."
            )

        users = User.objects.filter(id__in=user_ids)
        found_user_ids = set(
            users.values_list("id", flat=True)
        )

        invalid_user_ids = set(user_ids) - found_user_ids

        if invalid_user_ids:
            raise ValidationError(
                "One or more participant IDs are invalid."
            )

        existing_user_ids = set(
            Participant.objects.filter(
                conversation=conversation,
                user_id__in=user_ids,
            ).values_list("user_id", flat=True)
        )

        new_user_ids = [
            user_id
            for user_id in user_ids
            if user_id not in existing_user_ids
        ]

        Participant.objects.bulk_create([
            Participant(
                conversation=conversation,
                user_id=user_id,
            )
            for user_id in new_user_ids
        ])

        return conversation

    @staticmethod
    def remove_participants(conversation, user_ids):
        if conversation.type != ConversationType.GROUP:
            raise ValidationError(
                "Participants can only be removed from group conversations."
            )

        user_ids = set(user_ids)

        participant_user_ids = set(
            Participant.objects.filter(
                conversation=conversation,
                user_id__in=user_ids,
            ).values_list("user_id", flat=True)
        )

        invalid_user_ids = user_ids - participant_user_ids

        if invalid_user_ids:
            raise ValidationError(
                "One or more users are not participants in this conversation."
            )

        deleted_count, _ = Participant.objects.filter(
            conversation=conversation,
            user_id__in=participant_user_ids,
        ).delete()

        return {
            "deleted_count": deleted_count,
            "conversation": conversation,
        }



