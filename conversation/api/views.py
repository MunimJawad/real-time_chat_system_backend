from django.shortcuts import render
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.
def home(request):
    return JsonResponse({"message": "Hello World!"})



#next week Create conversation, read each conversation, add participants system, create message or update message.