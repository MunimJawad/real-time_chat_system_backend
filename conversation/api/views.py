from django.db.models import Model
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q, Prefetch
import conversation
from conversation.services.create_conversation import (
CreateConversation
)
from conversation.models import ConversationType, Participant
from rest_framework import status
from django.core.exceptions import BadRequest
from conversation.api.serializers import (
ParticipantSerializer, ConversationSerializer
)
from conversation.models import Conversation
from common.response import success_response, error_response

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
                    queryset=Participant.objects.select_related("user")
                )
            )
            .distinct()
        )

        serializer = ConversationSerializer(conversations, many=True)

        return success_response(data=serializer.data, message="Conversation list successfully.", status_code=status.HTTP_200_OK)

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


#next week add and remove participants in conversations, leave from group conversation,delete conversations,
#add pagination in conversation list and  conversation detail with messages,
# create message or update message in conversation, search conversations and messages in there pages.