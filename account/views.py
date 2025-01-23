from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, ForgetPasswordSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import OTP
from random import randint
from django.core.mail import send_mail


class AccountRegistrationView(APIView):
    def post(self, request):
        """
        Register a new account with valid data. 
        """
        data = request.data
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "status": "success",
                "token": str(token)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    'status': "failed",
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class AccountLoginView(APIView):
    def post(self, request):
        """
        Login to an account with valid data.
        """
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "status": "success",
                "token": str(token)
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                'status': "failed",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):
    def post(self, request):
        """
            Set OTP to the OTP model if user with email exist
        """
        data = request.data
        serializer = ForgetPasswordSerializer(
            data=data)  # Validate the data and email
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            otp = randint(1000, 9999)  # Generate OTP
            # Checking if a user with OTP Exist
            is_exist = OTP.objects.filter(user=user).exists()
            if is_exist:
                otp_model = OTP.objects.get(user=user)
                otp_model.otp = otp  # If exist update the OTP
                otp_model.save()
            else:
                # If new user Create OTP Model
                OTP.objects.create(user=user, otp=otp)
            send_mail("OTP for changing password",
                      f"Your OTP is {otp}", "ahmedsalauddin677785@gmail.com", [user.email])  # Send mail
            return Response({
                "status": "success",
                "details": "OTP send successful"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
