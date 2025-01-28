from .serializers import RegistrationSerializer, LoginSerializer, ForgetPasswordSerializer, VerifyOtpSerializer
from django.core.mail import send_mail
from random import randint
from .models import OTP
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import RegistrationSerializer, LoginSerializer, ForgetPasswordSerializer, ResetPasswordSerializer,CustomPermissionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import pdb
from django.contrib.auth.models import Group,Permission

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
            user = get_user_model().objects.get(username=username)
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
            user = get_user_model().objects.get(
                email=serializer.validated_data['email'])
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


class ResetPasswordView(APIView):
    def post(self, request):
        """
            Reset password for valid user with valid email address
        """
        data = request.data
        serializer = ResetPasswordSerializer(data=data)  # validate the request
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = get_user_model().objects.get(email=email)
            user.set_password(password)  # Change password
            user.save()
            token_exist = Token.objects.filter(user=user).exists()
            if token_exist:  # Delete previous token if exist
                token = Token.objects.get(user=user)
                token.delete()
            # Create new token and return
            token = Token.objects.create(user=user)
            return Response({
                "status": "success",
                "token": str(token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': "failed",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("OTP")

        try:
            email_record = OTP.objects.get(user__email=email)
            otp_record = OTP.objects.get(otp=otp)

            serializer = VerifyOtpSerializer(data={
                "email": email_record.user.email,
                "otp": otp_record.otp
            })

            if serializer.is_valid():
                email = serializer.validated_data["email"]
                otp_object = OTP.objects.get(user__email=email)
                otp_object.delete()
                return Response(
                    {
                        "status": "success",
                        "can_change_pass": True,
                        "details": None
                    }
                )
            else:
                return Response(
                    {
                        "status": "failed",
                        "can_change_pass": False,
                        "details": serializer.errors
                    },
                    status=400
                )
        except OTP.DoesNotExist:
            return Response(
                {
                    "status": "failed",
                    "can_change_pass": False,
                    "details": "Invalid email or OTP."
                },
                status=404
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "can_change_pass": False,
                    "details": str(e)
                },
                status=500
            )

class CustomPermissionView(APIView):
    def post(self, request):
        data = request.data
        serializer = CustomPermissionSerializer(data=data)
        
        if serializer.is_valid():
            permission=serializer.save()
            name = serializer.validated_data["name"]
            
            return Response({
                "id": permission.id,  
                "permission_name": name
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            {
                "errors":serializer.errors
            }
            , status=status.HTTP_400_BAD_REQUEST)