
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q, Prefetch

from conversation.services.create_conversation import (
CreateConversation
)
from conversation.models import ConversationType, Participant
from rest_framework import status
from django.core.exceptions import BadRequest, ValidationError, PermissionDenied
from conversation.api.serializers import (
ParticipantSerializer, ConversationSerializer, AddParticipantSerializer
)
from conversation.models import Conversation
from common.response import success_response, error_response
from common.pagination import paginate_queryset

# Create your views here.
def home(request):
    return JsonResponse({"message": "Hello World!"})





class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = (
            Conversation.objects
            .filter(
                Q(participants__user=request.user) |
                Q(created_by=request.user)
            )
            .select_related("created_by")
            .prefetch_related(
                Prefetch(
                    "participants",
                    queryset=Participant.objects.select_related("user", "user__profile")
                )
            )
            .distinct().order_by("-updated_at")
        )

        data = paginate_queryset(queryset=conversations, request=request, view= self, serializer_class=ConversationSerializer, context={"request": request})

        return success_response(data=data, message="Conversation list successfully.", status_code=status.HTTP_200_OK)


    def post(self, request):
        conversation_type = request.data.get("type")

        if conversation_type == ConversationType.DIRECT:
            conversation = CreateConversation.direct_conversation(request)

        elif conversation_type == ConversationType.GROUP:
            conversation = CreateConversation.group_conversation(request)

        else:
            raise BadRequest("Invalid conversation type.")

        participants = ParticipantSerializer(
            conversation.participants.all(),
            many=True
        ).data

        data = {
                "id": conversation.id,
                "type": conversation.type,
                "name": conversation.name,
                "participants": participants
            }

        return success_response(data=data, message="Conversation get or created successfully.", status_code=status.HTTP_200_OK)

from conversation.services.add_remove_participants import ParticipantService
class AddParticipantView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise ValidationError("Conversation does not exist.")

        is_admin = Participant.objects.filter(
            conversation=conversation,
            user=request.user,
            is_conversation_admin=True,
        ).exists()

        if not is_admin:
            raise PermissionDenied(
                "You do not have permission to add participants."
            )

        serializer = AddParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = ParticipantService.add_participants(conversation,
                                                     user_ids=serializer.validated_data["participant_ids"]
                                                     )

        participants = ParticipantSerializer(
            result.participants.select_related("user"),
            many=True
        ).data

        data = {
            "id": result.id,
            "type": result.type,
            "name": result.name,
            "participants": participants
        }
        return success_response(data=data, message="Participants added successfully.",
                                status_code=status.HTTP_200_OK)


class RemoveParticipantView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise ValidationError("Conversation does not exist.")

        is_admin = Participant.objects.filter(
            conversation=conversation,
            user=request.user,
            is_conversation_admin=True,
        ).exists()

        if not is_admin:
            raise PermissionDenied(
                "You do not have permission to remove participants."
            )

        serializer = AddParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = ParticipantService.remove_participants(conversation,
                                                        user_ids=serializer.validated_data["participant_ids"]
                                                        )
        participants = ParticipantSerializer(
            result["conversation"].participants.select_related("user"),
            many=True
        ).data

        data = {
            "deleted_count": result["deleted_count"],
            "id": result["conversation"].id,
            "type": result["conversation"].type,
            "name": result["conversation"].name,
            "participants": participants
        }
        return success_response(data=data, message="Participants removed successfully.",
                                status_code=status.HTTP_200_OK)




# leave from group conversation,delete conversations,
# conversation detail with messages,
# create message or update message in conversation, search conversations and messages in there pages.


