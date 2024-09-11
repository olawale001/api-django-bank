from dataclasses import fields
import email
from os import error
from re import T
import token
from django.forms import ValidationError
from rest_framework import serializers
from .models import User, ForgetPassword
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.core import exceptions
# from utils.utility import send_otp
from django.shortcuts import get_object_or_404
from django.utils import timezone

class SignUpUserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    confirmed_password= serializers.CharField(read_only=True, max_length=50)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'phone',
            'password',
            'confirmed_password',
            'email',
            'is_verified',
            'date_joined',
            'token'
        ]
        read_only_fields = ['id', 'is_verified', 'date_joined', 'token']

        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'confirmed_password': {'write_only': True, 'required': True},
        }

        def validate(self, data):
            error = {}
            confirmed_password = data.get('confirmed_password', '')
            password = data.get('password', '')
            email = data.get('email', '')

            if password.lower() != confirmed_password.lower():
                error['confirmed_password'] = ['password must match']
            try:
                validate_password(password=password) and validate_password(password=confirmed_password)    
            except exceptions.ValidationError as e:
                error['password'] = list(e.messages)    

            email_ = User.objects.filter(email__iexact=email)    
            if email.exicts():
                error['email'] = ['Email is already exicts']

            if error:
                raise ValidationError(error)    
            return data
        
        def create(self, validated_data):
            validated_data.pop('confirmed_password')
            user = User.objects.create_user(**validated_data)
            send_otp(user, validated_data.get('emai'), 'Email verification')
            token, _ = Token.objects.get_or_create(user=user)
            self.token = token.key
            return user
        
        def to_representation(self, instance):
            data = super().to_representation(instance)
            if hasattr(self,'token'):
                data['token'] = self.token
            return data
        

class LoginUserSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
        token = serializers.CharField(read_only=True)

        def validate(self, data):
            email = data.get('email', '')
            password = data.get('password', '')
            
            if not email or not password:
                raise serializers.ValidationError("Please provide both email and password")
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this email does not exist")
            print(f"Stored password: {user.password}")
            print(f"Provided password: {password}")
            
            if not user.check_password(password):
                raise serializers.ValidationError("Password is not correct")
            
            
            user = authenticate(email=user.email, password=password)

            if not user:
                raise serializers.ValidationError("Authentication failed. Please check your email and password")

            token, _ = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            data['user'] = user
            return data

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)    
    otp = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email', '')
        otp = data.get('otp', '')

        user = get_object_or_404(User, email__iexact=email)
        try:
            forget_password = get_object_or_404(ForgetPassword, user=user, otp=otp)
        except ForgetPassword.DoesNotExist:
            raise serializers.ValidationError({'otp': 'Invalid otp or otp does not exist'})
        
        if timezone.now() > forget_password.created_at + timezone.timedelta(minutes=15):
            raise serializers.ValidationError({'OTP':'otp has expired'})
        return data
    
    def save(self, **kwargs):
        email = self.validated_data.get('email')
        user = get_object_or_404(User, email__iexact=email)
        if not user.is_verified:
            user.is_verified = True
            user.save()
        return user
    

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def validate_email(self, data):
        if not User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('Email does not exist')
        return data
    
    def save(self, **kwargs):
        email= self.validate_email['email']
        user = get_object_or_404(User, email__iexact=email)
        send_otp(user, email, 'Reset Password')
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    confirmed_password = serializers.CharField(required=T, write_only=True)

    def validate(self, data):
        email = data.get('email', '')
        otp = data.get('otp', '')
        password = data.get('password', '')
        confirmed_password = data.get('confirmed_password', '')

        if password != confirmed_password:
            raise serializers.ValidationError({'password': 'password and confirmed password does not match'})
        user = get_object_or_404(User, email__iexact=email)
        forget_password = get_object_or_404(ForgetPassword, user=user, otp=otp)
        if timezone.now() > forget_password.created_at + timezone.timedelta(minutes=15):
            raise serializers.ValidationError({'OTP': 'otp is expired'})
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
                
        return data
    
    def save(self):
        email = self.validated_data['email']
        password = self.validated_data['password']
        user = get_object_or_404(User, email__iexact=email)
        user.set_password(password)
        user.save()
        return user
