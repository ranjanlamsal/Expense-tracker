from django.shortcuts import render
from rest_framework import generics, status
from .serializer import RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings


class RegisterView(generics.GenericAPIView):
    
    serializer_class = RegisterSerializer
    
    def post(self, request):
        user = request.data
        
        serializer = self.serializer_class(data = user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        user_data = serializer.data
        
        user = User.objects.get(email = user_data['email'])
        
        token = RefreshToken.for_user(user).access_token
        
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+'?token='+str(token)
        email_body = 'Hi, '+user.username+'. Use link below to verify your account on Expense-Tracker.\n\n'+ absurl
        
        data = {
            'email_subject': 'Verify Your Email',
            'email_body':email_body,
            'to_email': user.email}
        Util.send_email(data)
        
        
        return Response(user_data, status=status.HTTP_201_CREATED)
    

class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get('token')
        # SECRET_KEY = GetEnv.get_secret_key()
        try:
            token_obj = AccessToken(token)
            user_id = token_obj['user_id']
            user = User.objects.get(id=user_id)
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
            
            return Response({'email': 'Successfully Activated'}, status=status.HTTP_200_OK)
    
        except TokenError as e:
                    return Response({'error': 'Invalid or Expired Token'}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):        
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception= True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)