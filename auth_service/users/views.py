from django.shortcuts import render
import jwt, datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User


# Create your views here.


SECRET = 'your-secret-key-change-in-prod'

def make_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email exists'}, status=400)
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password']
        )
        token = make_token(user.id, user.email)
        return Response({'token': token, 'user_id': user.id}, status=201)

class LoginView(APIView):
    def post(self, request):
        from django.contrib.auth import authenticate
        user = authenticate(
            username=request.data['email'],
            password=request.data['password']
        )
        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)
        token = make_token(user.id, user.email)
        return Response({'token': token, 'user_id': user.id})

class VerifyTokenView(APIView):
    """Called by other microservices to validate a JWT"""
    def post(self, request):
        token = request.data.get('token', '')
        try:
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            return Response({'valid': True, 'user_id': payload['user_id'],
                             'email': payload['email']})
        except jwt.ExpiredSignatureError:
            return Response({'valid': False, 'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'valid': False, 'error': 'Invalid token'}, status=401)