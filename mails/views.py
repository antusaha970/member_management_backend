from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from rest_framework.response import Response
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from rest_framework import status


logger = logging.getLogger("myapp")


class SetMailConfigurationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            serializer = serializers.SMTPConfigurationSerializer(
                data=request.data)
            if serializer.is_valid():
                return Response("Ok")
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Create",
                    severity_level="info",
                    description="User tried to create a mail configuration but faced an error",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=400)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Create",
                severity_level="info",
                description="User tried to create a mail configuration but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
