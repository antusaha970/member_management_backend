from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import ActivityLog
from .serializers import AdminActivityLogSerializer, NormalUserActivityLogSerializer
import logging

logger = logging.getLogger("myapp")


class ActivityLogAPIView(APIView):
    """API View to fetch user activities."""
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        try:
            user = request.user  
            activity_logs = ActivityLog.objects.filter(user=user)

            if not activity_logs.exists():
                return Response({
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "No activity logs found for this user.",
                    "status": "failed",
                    "data": []
                }, status=status.HTTP_404_NOT_FOUND)
            if user.is_superuser:
                serializer = AdminActivityLogSerializer(activity_logs, many=True)
            else:
                serializer = NormalUserActivityLogSerializer(activity_logs, many=True)

            return Response({
                "code": status.HTTP_200_OK,
                "message": f"{user.username} retrieved logged data successfully",
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(str(e))  
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while retrieving activity logs.",
                "status": "failed",
                "errors": {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
