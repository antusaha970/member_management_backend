from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from member.models import Member
from .utils.filters import MemberFilter
from restaurant.models import Restaurant
from product.models import Product
from event.models import Event


import logging
logger = logging.getLogger("myapp")


class DashboardCardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            total_member = Member.objects.all()
            total_active_member = Member.objects.filter(
                membership_status__name__iexact="active")
            total_pending_member = Member.objects.filter(
                membership_status__name__iexact="pending")
            total_restaurants = Restaurant.active_objects.all()
            total_products = Product.objects.filter(is_active=True)
            total_events = Event.objects.filter(is_active=True)

            total_member_filterset = MemberFilter(
                request.GET, queryset=total_member)
            total_active_member_filterset = MemberFilter(
                request.GET, queryset=total_active_member)
            total_pending_member_filterset = MemberFilter(
                request.GET, queryset=total_pending_member)
            total_restaurants_filterset = MemberFilter(
                request.GET, queryset=total_restaurants)
            total_products_filterset = MemberFilter(
                request.GET, queryset=total_products)
            total_events_filterset = MemberFilter(
                request.GET, queryset=total_events)

            total_member = total_member_filterset.qs
            total_active_member = total_active_member_filterset.qs
            total_pending_member = total_pending_member_filterset.qs
            total_restaurants = total_restaurants_filterset.qs
            total_products = total_products_filterset.qs
            total_events = total_events_filterset.qs

            total_member_count = total_member.count()
            total_active_member_count = total_active_member.count()
            total_pending_member_count = total_pending_member.count()
            total_restaurants_count = total_restaurants.count()
            total_products_count = total_products.count()
            total_events_count = total_events.count()

            return Response({
                "code": 200,
                "status": "success",
                "message": "All dashboard card data",
                "data": {
                    "total_member_count": total_member_count,
                    "total_active_member_count": total_active_member_count,
                    "total_pending_member_count": total_pending_member_count,
                    "total_restaurants_count": total_restaurants_count,
                    "total_products_count": total_products_count,
                    "total_events_count": total_events_count,
                }
            }, status=200)

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Error while viewing all users",
                severity_level="error",
                description="Error while viewing all users",
            )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
