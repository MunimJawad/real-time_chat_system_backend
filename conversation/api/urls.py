from django.urls import path
from . import views
urlpatterns = [
    path('', views.home),
    path('conversations/', views.ConversationView.as_view()),
]