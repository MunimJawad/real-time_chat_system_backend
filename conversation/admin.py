from django.contrib import admin
from . import models
from .models import Conversation

# Register your models here.

admin.site.register(models.Conversation)
admin.site.register(models.Participant)
admin.site.register(models.Message)

