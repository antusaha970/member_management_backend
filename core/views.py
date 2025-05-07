from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from .models import *
from member.utils.utility_functions import generate_member_id
import pdb
from member.utils.permission_classes import AddMemberPermission
from rest_framework.exceptions import ValidationError, PermissionDenied


class MembershipTypeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

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

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
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
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code) 


class MembershipStatusChoiceViewSet(ModelViewSet):
    serializer_class = MembershipStatusChoiceSerializer
    queryset = MembershipStatusChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)

class MaritalStatusChoiceViewSet(ModelViewSet):
    serializer_class = MaritalStatusChoiceSerializer
    queryset = MaritalStatusChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)


class EmploymentTypeChoiceViewSet(ModelViewSet):
    serializer_class = EmploymentTypeChoiceSerializer
    queryset = EmploymentTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)

class EmailTypeChoiceViewSet(ModelViewSet):
    serializer_class = EmailTypeChoiceSerializer
    queryset = EmailTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)

        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)

class ContactTypeChoiceViewSet(ModelViewSet):
    serializer_class = ContactTypeChoiceSerializer
    queryset = ContactTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
        
    def handle_exception(self, exc):
            response = super().handle_exception(exc)
            if response.status_code == 401:
                return response
            # Reformat only known types  validation and permission errors
            if isinstance(exc, (ValidationError, PermissionDenied)):
                return Response(response.data, status=response.status_code)
class AddressTypeChoiceViewSet(ModelViewSet):
    serializer_class = AddressTypeChoiceSerializer
    queryset = AddressTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)


class DocumentTypeChoiceViewSet(ModelViewSet):
    serializer_class = DocumentTypeChoiceSerializer
    queryset = DocumentTypeChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)


class SpouseStatusChoiceViewSet(ModelViewSet):
    serializer_class = SpouseStatusChoiceSerializer
    queryset = SpouseStatusChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)



class DescendantRelationChoiceViewSet(ModelViewSet):
    serializer_class = DescendantRelationChoiceSerializer
    queryset = DescendantRelationChoice.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code == 401:
            return response
        # Reformat only known types  validation and permission errors
        if isinstance(exc, (ValidationError, PermissionDenied)):
            return Response(response.data, status=response.status_code)
