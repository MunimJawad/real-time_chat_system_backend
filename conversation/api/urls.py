from django.urls import path
from . import views
urlpatterns = [
    path('', views.home),
    path('conversations/', views.ConversationView.as_view()),
    path('add-participants/<int:conversation_id>/', views.AddParticipantView.as_view()),
   path('remove-participants/<int:conversation_id>/', views.RemoveParticipantView.as_view()),
]