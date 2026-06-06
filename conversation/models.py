from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ConversationType(models.TextChoices):
    DIRECT = "DIRECT", "Direct"
    GROUP = "GROUP", "Group"


class MessageType(models.TextChoices):
    TEXT = "TEXT", "Text"
    IMAGE = "IMAGE", "Image"
    FILE = "FILE", "File"
    VOICE = "VOICE", "Voice"

class Conversation(BaseModel):
    type = models.CharField(
        max_length=20,
        choices=ConversationType,
        default=ConversationType.DIRECT,
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_conversation")
    name = models.CharField(max_length=200, null=True, blank=True)#group chat name

    class Meta:
        db_table = "conversation"
        ordering= ["-created_at"]

    def __str__(self):
        return f"{self.created_by} - {self.type}----{self.name}"


class Participant(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    is_conversation_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "participants"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "conversation"],
                name="unique_conversation_participants",
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["conversation"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.conversation_id}"


class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")

    message_type = models.CharField(max_length=20, choices=MessageType, default=MessageType.TEXT)
    content = models.TextField()
    is_edited = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "message"
        ordering= ["created_at"]

        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self):
        return f"Message {self.id}---{self.sender}"

