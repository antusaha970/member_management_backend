from core.utils.pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAdminUser
from activity_log.utils.permission_classes import AllUserActivityLogPermission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ActivityLog
from .serializers import AdminActivityLogSerializer, NormalUserActivityLogSerializer, AllUserActivityLogSerializer
import logging
logger = logging.getLogger("myapp")


class ActivityLogAPIView(APIView):
    """API View to fetch user activities."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            activity_logs = ActivityLog.objects.filter(
                user=user).order_by('id')

            if not activity_logs.exists():
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "No activity logs found for this user.",
                    "status": "failed",
                    "data": []
                }, status=status.HTTP_404_NOT_FOUND)

            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                activity_logs, request, view=self)

            if user.is_superuser:
                serializer = AdminActivityLogSerializer(
                    paginated_queryset, many=True)
            else:
                serializer = NormalUserActivityLogSerializer(
                    paginated_queryset, many=True)

            return paginator.get_paginated_response({
                "code": status.HTTP_200_OK,
                "message": f"{user.username} retrieved logged data successfully",
                "status": "success",
                "data": serializer.data

            }, status=200)

        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while retrieving activity logs.",
                "status": "failed",
                "errors": {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllUserActivityLogAPIView(APIView):
    """API View to fetch all user activities."""
    permission_classes = [IsAuthenticated, AllUserActivityLogPermission]

    def get(self, request):
        try:

            activity_logs = ActivityLog.objects.all().order_by('id')
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                activity_logs, request, view=self)
            serializer = AllUserActivityLogSerializer(
                paginated_queryset, many=True)

            response = paginator.get_paginated_response({
                "code": status.HTTP_200_OK,
                "message": "All user activity logs retrieved successfully",
                "status": "success",
                "data": serializer.data
            }, status=200)
            return response

        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while retrieving all activity logs.",
                "status": "failed",
                "errors": {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
