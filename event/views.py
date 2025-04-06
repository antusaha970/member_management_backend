

from django.shortcuts import render
from rest_framework.views import APIView
from event import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Venue
import logging
logger = logging.getLogger("myapp")

# Create your views here.
class EventVenueView(APIView):
    def post(self,request):
        try:
            data = request.data
            serializer = serializers.EventVenueSerializer(data=data)
            if serializer.is_valid():
                venue_instance=serializer.save()
                street_address = serializer.validated_data["street_address"]
                city = serializer.validated_data["city"]
                return Response({
                        "code": 201,
                        "message": "Venue created successfully",
                        "status": "success",
                        "data": {
                            "venue_id": venue_instance.id,
                            "street_address":street_address,
                            "city":city
                            
                        }
                        }, status=status.HTTP_201_CREATED)
            else:
               return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            venues = Venue.objects.all()
            serializer = serializers.EventVenueViewSerializer(venues, many=True)
            return Response({
                "code": 200,
                "message": "Venues retrieved successfully",
                "status": "success",
                "data": serializer.data  # no need for extra list wrapping
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
            

class EventView(APIView):
    def post(self,request):
        try:
            data = request.data
            serializer = serializers.EventSerializer(data=data)
            if serializer.is_valid():
                event_instance=serializer.save()
                event_title=serializer.validated_data["title"]
                return Response({
                        "code": 201,
                        "message": "Event created successfully",
                        "status": "success",
                        "data": {
                            "event_id": event_instance.id,
                            "event_title":event_title,
                            
                        }
                        }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)    
                
                
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
                 
                
                
        
        