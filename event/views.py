
from django.shortcuts import render
from rest_framework.views import APIView
from event import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Venue,Event,EventTicket,EventMedia,EventFee
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



# Create your views here.
class EventVenueView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self,request):
        """
        Creates a new event venue instance and logs an activity.
        Args:
            request (Request): The request containing the data for the new event venue instance.
        Returns:
            Response: The response containing the new event venue instance's id, street address and city
        """
        try:
            data = request.data
            serializer = serializers.EventVenueSerializer(data=data)
            if serializer.is_valid():
                venue_instance=serializer.save()
                street_address = serializer.validated_data["street_address"]
                city = serializer.validated_data["city"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Venue created successfully",
                    severity_level="info",
                    description="Venue created successfully for register a event",
                )
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
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Venue creation failed",
                    severity_level="error",
                    description="user tried to create a new venue but made an invalid request",
                )
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
                    verb="Venue creation failed",
                    severity_level="error",
                    description="user tried to create a new venue but made an invalid request",
                )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Retrieves a list of all event venues and logs an activity.
        Returns:
            Response: The response containing the list of event venues.
        """
        try:
            venues = Venue.objects.all()
            serializer = serializers.EventVenueViewSerializer(venues, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all venues",
                severity_level="info",
                description="User retrieved all venues successfully",)
            return Response({
                "code": 200,
                "message": "Venues retrieved successfully",
                "status": "success",
                "data": serializer.data  # no need for extra list wrapping
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Venues retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all venues",)
            
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class EventView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self,request):
        """
        Creates a new event instance and logs an activity.
        Args:
            request (Request): The request containing the data for the new event instance.
        Returns:
            Response: The response containing the new event instance's id and title
        """
        try:
            data = request.data
            serializer = serializers.EventSerializer(data=data)
            if serializer.is_valid():
                event_instance=serializer.save()
                event_title=serializer.validated_data["title"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event created successfully",
                    severity_level="info",
                    description="Event created successfully for register a event",)
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
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event creation failed",
                    severity_level="error",
                    description="user tried to create a new event but made an invalid request",)
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
                verb="Event creation failed",
                severity_level="error",
                description="user tried to create a new event but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Retrieves a list of all events and logs an activity.
        Returns:
            Response: The response containing the list of events.
        """
        try:
            events = Event.objects.all()
            serializer = serializers.EventViewSerializer(events, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all events",
                severity_level="info",
                description="User retrieved all events successfully",)
            return Response({
                "code": 200,
                "message": "Events retrieved successfully",
                "status": "success",
                "data": serializer.data  
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Events retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all events",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      

                 
class EventDetailView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get(self, request, event_id):
        """
        Retrieves a specific event by its event_id and logs an activity.
        Args:
            request (Request): The request object.
            event_id (int): The event_id of the event to retrieve.
        Returns:
            Response: The response containing the event details.
        """
        try:
            event = Event.objects.get(pk=event_id)
            serializer = serializers.EventViewSerializer(event)
            log_activity_task.delay_on_commit(
                
                request_data_activity_log(request),
                verb="Retrieve event details",
                severity_level="info",
                description="User retrieved event details successfully",)
            return Response({
                "code": 200,
                "message": "Event details retrieved successfully",
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Event details retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving specific event details",)
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Event not found",
                "status": "failed",
                "errors": {
                    "event": ["Event not found"]
                }})
                
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Event details retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving event details",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)] 
                }
            })
            
            
                        
class EventTicketView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self,request):
        """
        Creates a new event ticket and logs an activity.
        Args:
            request (Request): The request containing the data for the new event ticket instance.
        Returns:
            Response: The response containing the event ticket id and name.
        """
        try:
            data = request.data
            serializer = serializers.EventTicketSerializer(data=data)
            if serializer.is_valid():
                ticket_instance=serializer.save()
                ticket_name=serializer.validated_data["ticket_name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event ticket created successfully",
                    severity_level="info",
                    description="Event ticket created successfully for register a event",)
                return Response({
                        "code": 201,
                        "message": "Event ticket created successfully",
                        "status": "success",
                        "data": {
                            "ticket_id": ticket_instance.id,
                            "ticket_name": ticket_name
                        }})
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event ticket creation failed",
                    severity_level="error",
                    description="user tried to create a new event ticket but made an invalid request",)
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
                verb="Event ticket creation failed",
                severity_level="error",
                description="user tried to create a new event ticket but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Retrieves a list of all event tickets and logs an activity.
        Returns:
            Response: The response containing the list of event tickets.
        """
        try:
            event_ticket = EventTicket.objects.all()
            serializer = serializers.EventTicketViewSerializer(event_ticket, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all event tickets",
                severity_level="info",
                description="User retrieved all event tickets successfully",)
            return Response({
                "code": 200,
                "message": "Event tickets retrieved successfully",
                "status": "success",
                "data": serializer.data  
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Event tickets retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all event tickets",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
        
        
class EventMediaView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self,request):
        """
        Creates a new event media and logs an activity.
        Args:
            request (Request): The request containing the data for the new event media instance.
        Returns:
            Response: The response containing the event media id and name.
        """
        try:
            data = request.data
            serializer = serializers.EventMediaSerializer(data=data)
            if serializer.is_valid():
                media_instance=serializer.save()
                event_instance = serializer.validated_data["event"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event media created successfully",
                    severity_level="info",
                    description="Event media created successfully for register a event"
                    )
                return Response({
                        "code": 201,
                        "message": "Event media created successfully",
                        "status": "success",
                        "data": {
                            "image_id": media_instance.id,
                            "event_id": event_instance.id
                        }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event media creation failed",
                    severity_level="error",
                    description="user tried to create a new event media but made an invalid request",)
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
                verb="Event media creation failed",
                severity_level="error",
                description="user tried to create a new event media but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       
     
    def get(self, request):
        """
        Retrieves a list of all event medias and logs an activity.
        Returns:
            Response: The response containing the list of event medias.
        """
        try:
            event_media = EventMedia.objects.all()
            serializer = serializers.EventMediaViewSerializer(event_media, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all event medias",
                severity_level="info",
                description="User retrieved all event medias successfully",)
            return Response({
                "code": 200,
                "message": "Event medias retrieved successfully",
                "status": "success",
                "data": serializer.data  
            }, status=status.HTTP_200_OK)   
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Event medias retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all event medias",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EventFeeView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]   
    def post(self,request):
        """
        Creates a new event fee and logs an activity.
        Args:
            request (Request): The request containing the data for the new event fee instance.
        Returns:
            Response: The response containing the event fee id and fee.
        """
        try:
            data = request.data
            serializer = serializers.EventFeeSerializer(data=data)
            if serializer.is_valid():
                fee_instance=serializer.save()
                event_fee = serializer.validated_data["fee"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event fee created successfully",
                    severity_level="info",
                    description="Event fee created successfully for register a event",)
                return Response({
                        "code": 201,
                        "message": "Event fee created successfully",
                        "status": "success",
                        "data": {
                            "fee_id": fee_instance.id,
                            "event_fee": event_fee,
                            
                        }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Event fee creation failed",
                    severity_level="error",
                    description="user tried to create a new event fee but made an invalid request",)
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
                verb="Event fee creation failed",
                severity_level="error",
                description="user tried to create a new event fee but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    def get(self, request):
         """
         Retrieves a list of all event fees and logs an activity.
         Returns:
             Response: The response containing the list of event fees.
         """
         try:
            event_fees = EventFee.objects.all()
            serializer = serializers.EventFeeViewSerializer(event_fees, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all event fees",
                severity_level="info",
                description="User retrieved all event fees successfully",)
            return Response({
                "code": 200,
                "message": "Event fees retrieved successfully",
                "status": "success",
                "data": serializer.data  
            }, status=status.HTTP_200_OK)   
         except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Event fees retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all event fees") 
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
               
 

class EventTicketBuyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        Creates an invoice for an event ticket purchase.
        Args:
            request (Request): The request containing the data for the invoice instance.
        Returns:
            Response: The response containing the created invoice and a success message.
        """
        try:
            data = request.data
            serializer = serializers.EventTicketBuySerializer(data=data)
            if serializer.is_valid():
                
                member = serializer.validated_data["member_ID"]
                member = Member.objects.get(member_ID=member)
                event_ticket = serializer.validated_data["event_ticket"]
                
                invoice_type, _ = InvoiceType.objects.get_or_create(
                    name="Event")

                with transaction.atomic():
                    invoice = Invoice.objects.create(
                        currency="BDT",
                        invoice_number=generate_unique_invoice_number(),
                        balance_due=event_ticket.price,
                        paid_amount=0,
                        issue_date=date.today(),
                        total_amount=event_ticket.price,
                        is_full_paid=False,
                        status="unpaid",
                        invoice_type=invoice_type,
                        generated_by=request.user,
                        member=member,
                        event=event_ticket.event,
                    )
                    invoice_item = InvoiceItem.objects.create(
                        invoice=invoice
                    )
                    invoice_item.event_tickets.set([event_ticket.id])    
                    
                
                
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice created successfully",
                    severity_level="info",
                    description="user generated an invoice successfully",)
                return Response({
                    "code": 200,
                    "message": "Invoice created successfully",
                    "status": "success",
                    "data": InvoiceSerializer(invoice).data    
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice creation failed",
                    severity_level="error",
                    description="user tried to generate an invoice but made an invalid request",)
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
                verb="Invoice creation failed",
                severity_level="error",
                description="user tried to generate an invoice but made an invalid request",)
            return Response({

                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
                
            
                            
        
                     
        
        