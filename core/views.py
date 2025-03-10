from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import *
from member.utils.utility_functions import generate_member_id
import pdb

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

    def get(self, request):
        try:
            membership_types = MembershipType.objects.all()
            serializer = MembershipTypeViewSerializer(membership_types, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Membership type retrieve successful",
                "status": "success",
                "data": serializer.data},
                status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InstituteNameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = InstituteNameSerializer(data=data)

        if serializer.is_valid():
            inst_name = serializer.save()
            name = serializer.validated_data["name"]
            
            # return Response(, status=status.HTTP_201_CREATED)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Institute name created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(inst_name.id)
                    }
                },
                status=status.HTTP_201_CREATED)

        else:
            return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            inst_names = InstituteName.objects.all()
            serializer = InstituteNameViewSerializer(inst_names, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Institute names retrieve successful",
                "status": "success",
                "data": serializer.data},
                status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
            
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
            
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
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class MaritalStatusChoiceViewSet(ModelViewSet):
    serializer_class = MaritalStatusChoiceSerializer
    queryset = MaritalStatusChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class EmploymentTypeChoiceViewSet(ModelViewSet):
    serializer_class = EmploymentTypeChoiceSerializer
    queryset = EmploymentTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class EmailTypeChoiceViewSet(ModelViewSet):
    serializer_class = EmailTypeChoiceSerializer
    queryset = EmailTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class ContactTypeChoiceViewSet(ModelViewSet):
    serializer_class = ContactTypeChoiceSerializer
    queryset = ContactTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class AddressTypeChoiceViewSet(ModelViewSet):
    serializer_class = AddressTypeChoiceSerializer
    queryset = AddressTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class DocumentTypeChoiceViewSet(ModelViewSet):
    serializer_class = DocumentTypeChoiceSerializer
    queryset = DocumentTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class SpouseStatusChoiceViewSet(ModelViewSet):
    serializer_class = SpouseStatusChoiceSerializer
    queryset = SpouseStatusChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response


class DescendantRelationChoiceViewSet(ModelViewSet):
    serializer_class = DescendantRelationChoiceSerializer
    queryset = DescendantRelationChoice.objects.all()
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response

        # If there is a DRF validation error, reformat it
        if response is not None and isinstance(response.data, dict):
            errors = {field: messages for field,
                      messages in response.data.items()}
            
            return Response({
                "code": response.status_code,
                "message": "Operation failed",
                "status": "failed",
                'errors': errors}, status=response.status_code)
        return response
