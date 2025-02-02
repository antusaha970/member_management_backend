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
from rest_framework.permissions import IsAuthenticated
from account.utils.functions import clear_user_permissions_cache
from django.shortcuts import get_object_or_404

environ.Env.read_env()
env = environ.Env()


# Authentication views

class AccountRegistrationView(APIView):
    def post(self, request):
        """
        Register a new account with valid data. 
        """
        data = request.data
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid():
            remember_me = serializer.validated_data['remember_me']
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            response = Response({
                "status": "success",
                "token": str(token)
            }, status=status.HTTP_201_CREATED)

            # Add headers to prevent caching
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            # set cookie
            time_limit_for_cookie = 30 if remember_me == True else 7
            response.set_cookie(
                'auth_token',
                str(token),
                httponly=True,
                secure=env("COOKIE_SECURE") == "True",
                max_age=timedelta(days=time_limit_for_cookie).total_seconds()
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
            remember_me = serializer.validated_data['remember_me']
            user = get_user_model().objects.get(username=username)
            user.set_password(password)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)

            # Response with no-cache headers
            response = Response({
                "status": "success",
                "token": str(token)
            }, status=status.HTTP_200_OK)

            # Add headers to prevent caching
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            # set cookie
            time_limit_for_cookie = 30 if remember_me == True else 7
            response.set_cookie(
                'auth_token',
                str(token),
                httponly=True,
                secure=env("COOKIE_SECURE") == "True",
                max_age=timedelta(days=time_limit_for_cookie).total_seconds()
            )
            return response

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
                # initiate CELERY to send mail
                send_otp_mail_to_email.delay_on_commit(otp, user.email)
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

# Authentication views

# User views


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = get_user_model().objects.all()
            serializer = UserSerializer(data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupPermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = GroupModelSerializer(data=data)
        if serializer.is_valid():
            group = serializer.save()
            permissions = group.permission.all()
            permission_ids = [perm.id for perm in permissions]

            return Response({
                "group_id": group.id,
                "name": group.name,
                "permission": permission_ids
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            data = GroupModel.objects.all()
            serializer = GroupSerializerForViewAllGroups(data, many=True)
            return Response({
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, group_id):
        """Update a group with required permissions at least one permission"""
        group = get_object_or_404(GroupModel, pk=group_id)
        try:
            serializer = GroupModelSerializer(group, data=request.data)
            if serializer.is_valid():
                serializer.save()
                # after updating the group delete the permissions cache
                clear_user_permissions_cache()
                return Response({
                    'data': serializer.data
                })
            else:
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, group_id):
        """Delete a group"""
        group = get_object_or_404(GroupModel, pk=group_id)
        try:
            group.delete()
            # clear permissions cache for all users after a group deletion
            clear_user_permissions_cache()
            return Response({'detail': f"Group deleted successfully"})
        except Exception as e:
            return Response({
                'errors': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomPermissionView(APIView):
    permission_classes = [IsAuthenticated]
    # def get_permissions(self):
    #     # Assign method-specific permissions
    #     if self.request.method == 'POST':
    #         self.permission_classes = [IsAuthenticated, AddMemberPermission]
    #     elif self.request.method == 'GET':
    #         self.permission_classes = [IsAuthenticated]

    #     return super().get_permissions()
    def post(self, request):
        data = request.data
        serializer = CustomPermissionSerializer(data=data)

        if serializer.is_valid():
            permission = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "id": permission.id,
                "permission_name": name
            }, status=status.HTTP_201_CREATED)

        return Response(
            {
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            all_permission = PermissonModel.objects.all()

            serializer = CustomPermissionSerializerForView(
                all_permission, many=True)

            return Response(
                serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "errors": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssignGroupPermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
                "user_id": user.id,
                "groups": groups_data
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"detail": "User removed from group successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            data = AssignGroupPermission.objects.all()
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
            return Response({"data": users_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
