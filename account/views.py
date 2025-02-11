from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from .tasks import send_otp_email
from .serializers import RegistrationSerializer, LoginSerializer, ForgetPasswordSerializer, VerifyOtpSerializer
from django.core.mail import send_mail
from random import randint
from .models import OTP
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import RegistrationSerializer, LoginSerializer, ForgetPasswordSerializer, ResetPasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import pdb
from .tasks import send_otp_mail_to_email
import environ
from datetime import timedelta
from .permissions import HasCustomPermission
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from account.utils.functions import clear_user_permissions_cache, add_no_cache_header_in_response, generate_random_token
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from django.utils.datastructures import MultiValueDict
from .utils.permissions_classes import RegisterUserPermission
import logging
# set env
environ.Env.read_env()
env = environ.Env()
# Set logger
logger = logging.getLogger("myapp")
# Authentication views


class AccountRegistrationView(APIView):
    def post(self, request):
        """
        Register a new account with valid data. 
        """
        try:
            data = request.data
            serializer = RegistrationSerializer(data=data)
            if serializer.is_valid():
                remember_me = serializer.validated_data['remember_me']
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                response = Response({
                    "code": 201,
                    "message": "Operation successful",
                    "status": "success",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                }, status=status.HTTP_201_CREATED)

                # Add headers to prevent caching
                response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response["Pragma"] = "no-cache"
                response["Expires"] = "0"
                # set cookie
                time_limit_for_cookie = 30 if remember_me == True else 7

                response.set_cookie(
                    settings.SIMPLE_JWT["AUTH_COOKIE"],
                    str(refresh.access_token),
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    secure=env("COOKIE_SECURE") == "True",
                    max_age=timedelta(
                        days=time_limit_for_cookie).total_seconds()
                )
                response.set_cookie(
                    settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                    str(refresh),
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    secure=env("COOKIE_SECURE") == "True",
                    max_age=timedelta(
                        days=time_limit_for_cookie).total_seconds()
                )

                return response
            else:
                return Response(
                    {
                        'status': "failed",
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.exception(str(e))
            return Response({'errors': {
                'server_error': [str(e)]
            }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountLoginLogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Login to an account with valid data.
        """
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            if serializer.is_valid():
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                remember_me = serializer.validated_data['remember_me']
                user = get_user_model().objects.get(username=username)
                user.set_password(password)
                user.save()

                # Generate a new token on every login session
                refresh = RefreshToken.for_user(user)

                # Response with no-cache headers
                response = Response({
                    "status": "success",
                    "code": status.HTTP_200_OK,
                    "message": "Token was created successfully",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh)
                }, status=status.HTTP_200_OK)

                # Add headers to prevent caching
                response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response["Pragma"] = "no-cache"
                response["Expires"] = "0"
                # set cookie
                time_limit_for_cookie = 30 if remember_me == True else 7
                response.set_cookie(
                    settings.SIMPLE_JWT["AUTH_COOKIE"],
                    str(refresh.access_token),
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    secure=env("COOKIE_SECURE") == "True",
                    max_age=timedelta(
                        days=time_limit_for_cookie).total_seconds()
                )
                response.set_cookie(
                    settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                    str(refresh),
                    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                    secure=env("COOKIE_SECURE") == "True",
                    max_age=timedelta(
                        days=time_limit_for_cookie).total_seconds()
                )
                return response

            else:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status': "failed",
                    'message': "Invalid request",
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({'errors': {
                'code': status.HTTP_400_BAD_REQUEST,
                'status': "failed",
                'message': "Error occurred",
                'errors': {
                    "server_error": [str(e)]
                }
            }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """
        Delete authorization cookie from the server cookie
        """
        try:
            response = Response(
                {'code': status.HTTP_200_OK,
                 'status': "success",
                 'message': "Logout successful", 'detail': "Logout successful"}, status=status.HTTP_200_OK)
            # Delete the 'auth_token' cookie
            response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
            response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])

            # Add headers to prevent caching
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

            return response

        except Exception as e:
            logger.exception(str(e))
            return Response({'errors': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'status': "failed",
                'message': "Error occurred",
                'errors': {
                    "server_error": [str(e)]
                }
            }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForgetPasswordView(APIView):
    def post(self, request):
        """
            Set OTP to the OTP model if user with email exist
        """
        data = request.data
        serializer = ForgetPasswordSerializer(
            data=data)  # Validate the data and email
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = randint(1000, 9999)  # Generate OTP
            # Checking if a user with OTP Exist
            is_exist = ForgetPasswordOTP.objects.filter(email=email).exists()
            if is_exist:
                otp_model = ForgetPasswordOTP.objects.get(email=email)
                otp_model.expire_time = timezone.now()
                otp_model.otp = otp  # If exist update the OTP
                otp_model.save()
            else:
                # If new user Create OTP Model
                ForgetPasswordOTP.objects.create(email=email, otp=otp)
                # initiate CELERY to send mail
            send_otp_mail_to_email.delay_on_commit(otp, email)
            return Response({
                "status": "success",
                'code': status.HTTP_200_OK,
                'message': "OTP has been created successfully",
                "details": "OTP send successful"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                'code': status.HTTP_400_BAD_REQUEST,
                'message': "invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAuthenticated()]
        else:
            return [AllowAny()]

    def post(self, request):
        """
            Reset password for valid user with valid email address
        """
        data = request.data
        serializer = ResetPasswordSerializer(data=data)  # validate the request
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            pass_change_token = serializer.validated_data['token']
            forget_password_otp_obj = get_object_or_404(
                ForgetPasswordOTP, email=email)

            if pass_change_token != forget_password_otp_obj.token:
                return Response({
                    'code': status.HTTP_400_BAD_REQUEST,
                    'status': 'failed',
                    'message': "Error while matching token",
                    'detail': 'Token did not match',
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    with transaction.atomic():
                        user = get_user_model().objects.get(email=email)
                        user.set_password(password)  # Change password
                        user.save()
                        # Create new token and return
                        refresh = RefreshToken.for_user(user)
                        forget_password_otp_obj.delete()
                        response = Response({
                            "status": "success",
                            "code": status.HTTP_200_OK,
                            "message": "Operation successful",
                            "access_token": str(refresh.access_token),
                            "refresh_token": str(refresh)
                        }, status=status.HTTP_200_OK)
                        # set cookie
                        response.set_cookie(
                            settings.SIMPLE_JWT["AUTH_COOKIE"],
                            str(refresh.access_token),
                            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                            secure=env("COOKIE_SECURE") == "True",
                            max_age=timedelta(
                                days=7).total_seconds()
                        )
                        response.set_cookie(
                            settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                            str(refresh),
                            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                            secure=env("COOKIE_SECURE") == "True",
                            max_age=timedelta(
                                days=7).total_seconds()
                        )
                        return response
                except Exception as e:
                    logger.exception(str(e))
                    return Response({
                        "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "message": "Error occurred",
                        'status': 'failed', 'detail': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                'status': "failed",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):

        user = request.user
        serializer = UpdatePasswordSerializer(
            data=request.data, context={"user": user})

        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Password Updated successfully",
                "status": "success"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request data",
                "status": "failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    def post(self, request):
        """
            Verify OTP with given email here
        """
        data = request.data
        serializer = VerifyOtpSerializer(data=data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data['otp']
            forget_password_otp_obj = get_object_or_404(
                ForgetPasswordOTP, email=email)
            if forget_password_otp_obj.otp != otp:  # check if OTP matched
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Failed while verifying OTP",
                    "status": "failed",
                    "can_change_pass": False,
                    "details": "OTP didn't match"
                }, status=status.HTTP_400_BAD_REQUEST)

            if forget_password_otp_obj.is_expired():  # check if OTP has expired
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Failed while verifying OTP",
                    "status": "failed",
                    "can_change_pass": False,
                    "details": "OTP expired generate a new OTP"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                token = generate_random_token()
                forget_password_otp_obj.token = token
                forget_password_otp_obj.save(update_fields=['token'])
                return Response({
                    "code": status.HTTP_200_OK,
                    "message": "Operation successful",
                    "status": "success",
                    "can_change_pass": True,
                    "details": "Generated new Token for changing password",
                    "token": token
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.exception(str(e))
                return Response({
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Error occurred",
                    "status": "failed",
                    'errors': {'server_error': [str(e)]}

                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom refresh view to set the new refresh token in cookies
    """

    def post(self, request, *args, **kwargs):

        # Extract the refresh token from the request cookies
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])

        if not refresh_token:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Error while getting refresh token",
                "errors": {
                    "refresh_token": ["No refresh token provided"]
                }}, status=status.HTTP_400_BAD_REQUEST)

        request.data.update({'refresh': refresh_token})
        # Proceed with refresh process (generates new access & refresh tokens)
        response = super().post(request, *args, **kwargs)

        # Handle error responses (e.g., invalid or expired token)
        if response.status_code == 400:
            return Response({
                "code": 400,
                "status": "failed",
                "message": response.data,
                "errors": {
                    "token": ["failed to get refresh token"]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # If refresh token is generated, blacklist the old one
        if "refresh" in response.data:
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
                response.data["refresh"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                secure=env("COOKIE_SECURE") == "True",
                max_age=timedelta(
                    days=15).total_seconds()
            )

        # Set the new access token in cookie
        if "access" in response.data:
            response.set_cookie(
                settings.SIMPLE_JWT["AUTH_COOKIE"],
                response.data['access'],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                secure=env("COOKIE_SECURE") == "True",
                max_age=timedelta(
                    days=7).total_seconds()
            )

        response.data.pop("access")
        response.data.pop("refresh")
        response.data.update(
            {"code": 200, "status": "success", "message": "new access token given in cookie"})

        return response

    def handle_exception(self, exc):
        """
        Modify error messages for invalid/blacklisted tokens.
        """
        if isinstance(exc, InvalidToken):
            return Response({
                "code": 401,
                "status": "failed",
                "message": "invalid request",
                "errors": {
                    "token": ["Your refresh token is invalid or has been blacklisted."]
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        return super().handle_exception(exc)

# Authentication views

# User views


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            data = get_user_model().objects.filter(club=user.club)
            serializer = UserSerializer(data, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                'errors': {
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Error occurred",
                    "status": "failed",
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupPermissionView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = GroupModelSerializer(
                data=data, context={'user': request.user})
            if serializer.is_valid():
                group = serializer.save()
                permissions = group.permission.all()
                permission_ids = [perm.id for perm in permissions]

                return Response({
                    "code": status.HTTP_201_CREATED,
                    "message": "Operation successfully",
                    "status": "success",
                    "group_id": group.id,
                    "name": group.name,
                    "permission": permission_ids
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "invalid request",
                    "status": "failed",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "invalid request",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            user = request.user
            data = GroupModel.objects.filter(club=user.club)
            serializer = GroupSerializerForViewAllGroups(data, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "operation successful",
                "status": "success",
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, group_id):
        """Update a group with required permissions at least one permission"""
        group = get_object_or_404(GroupModel, pk=group_id)
        try:
            user = request.user
            serializer = GroupModelSerializer(
                group, data=request.data, context={'user': user})
            if serializer.is_valid():
                serializer.save()
                # after updating the group delete the permissions cache
                clear_user_permissions_cache()
                return Response({
                    "code": status.HTTP_200_OK,
                    "message": "Operation successful",
                    "status": "success",
                    'data': serializer.data
                })
            else:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, group_id):
        """Delete a group"""
        group = get_object_or_404(GroupModel, pk=group_id)
        try:
            group.delete()
            # clear permissions cache for all users after a group deletion
            clear_user_permissions_cache()
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Operation successful",
                "status": "success",
                'detail': f"Group deleted successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomPermissionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            data = request.data
            serializer = CustomPermissionSerializer(data=data)

            if serializer.is_valid():
                permission = serializer.save()
                name = serializer.validated_data["name"]

                return Response({
                    "code": status.HTTP_201_CREATED,
                    "message": "Operation successful",
                    "status": "success",
                    "id": permission.id,
                    "permission_name": name
                }, status=status.HTTP_201_CREATED)

            return Response(
                {
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                "errors": {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            all_permission = PermissonModel.objects.all()

            serializer = CustomPermissionSerializerForView(
                all_permission, many=True)

            return Response(
                {
                    "code": status.HTTP_200_OK,
                    "message": "Operation successful",
                    "status": "success",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                "errors": {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssignGroupPermissionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            data = request.data
            serializer = AssignGroupPermissionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                group = serializer.validated_data.get("group")
                user = serializer.validated_data.get("user")

                groups_data = []
                for gro in group:
                    groups_data.append(
                        {"group_id": gro.id, "group_name": gro.name})
                clear_user_permissions_cache()
                return Response({
                    "code": status.HTTP_201_CREATED,
                    "message": "Operation successful",
                    "status": "success",
                    "user_id": user.id,
                    "groups": groups_data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {'server_error': [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            serializer = DeleteUserFromGroupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data['user_id']
                group = serializer.validated_data['group_id']
                assign_group = AssignGroupPermission.objects.get(user=user)
                assign_group.group.remove(group)
                assign_group.save()
                clear_user_permissions_cache()
                return Response({
                    "code": status.HTTP_200_OK,
                    "message": "Operation successful",
                    "status": "success",
                    "detail": "User removed from group successfully."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    "server_error": [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            current_user = request.user
            data = AssignGroupPermission.objects.filter(
                user__club=current_user.club)
            users_data = []
            for assign_group in data:
                user_info = {
                    "user_id": assign_group.user.id if assign_group.user else None,
                    "username": assign_group.user.username if assign_group.user else "No User",
                    "groups": []
                }
                for group in assign_group.group.all():
                    group_info = {
                        "group_id": group.id,
                        "group_name": group.name,
                        "permissions": [
                            {"permission_id": perm.id, "permission_name": perm.name}
                            for perm in group.permission.all()
                        ]
                    }
                    user_info["groups"].append(group_info)
                users_data.append(user_info)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Operation successful",
                "status": "success",
                "data": users_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                "errors": {
                    "server_error": [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            user = data.get("user")
            group = data.get("group")
            if not user:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": {
                        "user": ["user field must be needed"]
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            if not group:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": {
                        "group": ["Group is must need"]
                    }}, status=status.HTTP_400_BAD_REQUEST)

            instance = AssignGroupPermission.objects.get(user=user)
            serializer = AssignGroupPermissionSerializer(
                instance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                user_id = serializer.validated_data["user"].id
                groups = serializer.validated_data["group"]
                groups_data = [{"group_id": gro.id,
                                "group_name": gro.name} for gro in groups]
                clear_user_permissions_cache()
                return Response({
                    "code": status.HTTP_200_OK,
                    "message": "Operation successful",
                    "status": "success",
                    "user_id": user_id,
                    "updated_groups": groups_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except AssignGroupPermission.DoesNotExist:
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                "errors": {"user": ["User not found in AssignGroupPermission"]}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                "errors":
                {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class AdminUserEmailView(APIView):
    permission_classes = [IsAuthenticated, RegisterUserPermission]

    def post(self, request):
        try:
            data = request.data
            if request.user.club is None:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": {
                        'club': ["You are not associated in club"]
                    }}, status=status.HTTP_404_NOT_FOUND)

            serializer = AdminUserEmailSerializer(
                data=data)
            if serializer.is_valid():
                instance = serializer.save()
                email = serializer.validated_data["email"]
                try:
                    otp = OTP.objects.get(email=email)
                    otp_value = otp.otp
                    send_otp_email.delay_on_commit(email, otp_value)

                except OTP.DoesNotExist:
                    return Response({
                        "code": status.HTTP_404_NOT_FOUND,
                        "message": "Invalid request",
                        "status": "failed",
                        "errors": {
                            'otp': ["OTP for the provided email does not exist."]
                        }}, status=status.HTTP_404_NOT_FOUND)

                response = Response({
                    "code": status.HTTP_201_CREATED,
                    "message": "Operation successful",
                    "status": "success",
                    "message": "OTP sent successfully",
                    "to": {
                        "email": email,
                    }
                }, status=status.HTTP_201_CREATED)
                # Add no cache header in response
                response = add_no_cache_header_in_response(response)
                return response

            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminUserVerifyOtpView(APIView):
    permission_classes = [IsAuthenticated, RegisterUserPermission]

    def post(self, request):
        try:
            data = request.data
            if request.user.club is None:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": {
                        'club': ["You are not associated in club"]
                    }}, status=status.HTTP_404_NOT_FOUND)

            serializer = AdminUserVerifyOtpSerializer(
                data=data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                otp = serializer.validated_data["otp"]
                otp_object = OTP.objects.get(email=email, otp=otp)
                otp_object.delete()
                try:
                    VerifySuccessfulEmail.objects.create(email=email)
                except Exception as e:
                    logger.exception(str(e))
                    return Response({
                        "code": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid request",
                        "status": "failed",
                        "errors": {
                            'email': [str(e)]
                        }}, status=status.HTTP_400_BAD_REQUEST)

                response = Response({
                                    "code": status.HTTP_200_OK,
                                    "message": "Operation successful",
                                    "status": "success",
                                    "email": email,
                                    }, status=status.HTTP_200_OK)
                # Add no cache header in response
                response = add_no_cache_header_in_response(response)
                return response

            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminUserRegistrationView(APIView):
    permission_classes = [IsAuthenticated, RegisterUserPermission]

    def post(self, request):
        try:
            data = request.data
            if request.user.club is None:
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "Invalid request",
                    "status": "failed",
                    "errors": {
                        "club": ["You are not associated in club"]
                    }}, status=status.HTTP_404_NOT_FOUND)

            club_id = request.user.club.id

            serializer = AdminUserRegistrationSerializer(
                data=data, context={"club_id": club_id})
            if serializer.is_valid():
                user = serializer.save()
                username = serializer.validated_data["username"]
                return Response({
                    "code": status.HTTP_201_CREATED,
                    "message": "Operation successful",
                    "status": "success",
                    "username": username
                }, status=status.HTTP_201_CREATED)

            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            data = AssignGroupPermission.objects.filter(user=user)
            users_data = []
            for assign_group in data:
                user_info = {
                    "user_id": assign_group.user.id if assign_group.user else None,
                    "username": assign_group.user.username if assign_group.user else "No User",
                    "groups": []
                }
                for group in assign_group.group.all():
                    group_info = {
                        "group_id": group.id,
                        "group_name": group.name,
                        "permissions": [
                            {"permission_id": perm.id, "permission_name": perm.name}
                            for perm in group.permission.all()
                        ]
                    }
                    user_info["groups"].append(group_info)
                users_data.append(user_info)
            response = Response({
                "code": status.HTTP_200_OK,
                "message": "Operation successful",
                "status": "success",
                "data": users_data},
                status=status.HTTP_200_OK)
            # add no cache header to response
            response = add_no_cache_header_in_response(response)
            return response
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid request",
                "status": "failed",
                "errors": {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
