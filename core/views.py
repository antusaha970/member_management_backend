from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import *


class MembershipTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = MembershipTypeSerializer(data=data)

        if serializer.is_valid():
            mem_type = serializer.save()
            name = serializer.validated_data["name"]
            return Response({
                "name": name,
                "id": str(mem_type.id)
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class InstituteNameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = InstituteNameSerializer(data=data)

        if serializer.is_valid():
            inst_name = serializer.save()
            name = serializer.validated_data["name"]
            return Response({
                "name": name,
                "id": str(inst_name.id)
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class GenderViewSet(ModelViewSet):
    serializer_class = GenderSerializer
    queryset = Gender.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response(
                {"errors": errors},
                status=response.status_code,
            )
        return response


class MembershipStatusChoiceViewSet(ModelViewSet):
    serializer_class = MembershipStatusChoiceSerializer
    queryset = MembershipStatusChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response(
                {"errors": errors},
                status=response.status_code,
            )
        return response
