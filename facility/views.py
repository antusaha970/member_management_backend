
from django.shortcuts import render
from rest_framework.views import APIView
from facility import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Facility,FacilityUseFee
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from activity_log.tasks import get_location, get_client_ip, log_activity_task
from activity_log.utils.functions import request_data_activity_log
from member_financial_management.utils.functions import generate_unique_invoice_number
from member.models import Member
from django.db import transaction
from member_financial_management.serializers import InvoiceSerializer
from member_financial_management.models import Invoice, InvoiceItem, InvoiceType
from datetime import date
import logging
logger = logging.getLogger("myapp")
import pdb


class FacilityView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self, request):
        """
        Creates a new facility instance and logs an activity.
        Args:
            request (Request): The request containing the data for the new facility instance.
        Returns:
            Response: The response containing the new facility instance's id and name
        """
        try:
            data = request.data
            serializer = serializers.FacilitySerializer(data = data)
            if serializer.is_valid():
                facility_instance = serializer.save()
                facility_name = serializer.validated_data["name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Facility created successfully",
                    severity_level="info",
                    description="Facility created successfully",)
                return Response({
                    "code": 201,
                    "message": "Facility created successfully",
                    "status": "success",
                    "data": {
                        "facility_id": facility_instance.id,
                        "facility_name": facility_name,
                    }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Facility creation failed",
                    severity_level="error",
                    description="user tried to create a new facility but made an invalid request",)
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Facility creation failed",
                severity_level="error",
                description="user tried to create a new facility but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self, request):
        """
        Retrieves a list of all facilities and logs an activity.
        Returns:
            Response: The response containing the list of facilities.
        """
        try:
            facilities = Facility.objects.all()
            serializer = serializers.FacilityViewSerializer(facilities, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all facilities",
                severity_level="info",
                description="User retrieved all facilities successfully",)
            return Response({
                "code": 200,
                "message": "Facilities retrieved successfully",
                "status": "success",
                "data": serializer.data  
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Facilities retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all facilities",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                
                
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        