from django.contrib import admin
from django.urls import path

from users.views import RegisterView, LoginView, VerifyTokenView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/',    LoginView.as_view()),
    path('auth/verify/',   VerifyTokenView.as_view()),  # internal endpoint
]