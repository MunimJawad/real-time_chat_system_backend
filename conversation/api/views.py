from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from conversation.services.create_conversation import (
CreateConversation
)
from conversation.models import ConversationType, Participant
from rest_framework import status
from django.core.exceptions import BadRequest
from conversation.api.serializers import (
ParticipantSerializer
)
from common.response import success_response, error_response

# Create your views here.
def home(request):
    return JsonResponse({"message": "Hello World!"})



#next week Create conversation, read each conversation, add participants system, create message or update message.

class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

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


