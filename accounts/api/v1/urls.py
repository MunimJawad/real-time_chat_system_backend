from django.urls import path
from accounts.api.v1 import views
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('', views.Home.as_view() ),
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('refresh/',TokenRefreshView.as_view()),

    path('profile/<int:profile_id>/', views.ProfileView.as_view()),

    path("pending-received-connections/", views.PendingReceivedConnectionsView.as_view()),
    path("pedning-sent-connections/", views.PendingSentConnectionsView.as_view()),
    path("connection-request/", views.ConnectionView.as_view()),
    path(
        "connection-update/<int:pk>/",
        views.ConnectionUpdateView.as_view()
    ),
]