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
                "code": status.HTTP_200_OK,
                "message": "Membership type created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(mem_type.id)
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
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
            code = serializer.validated_data["code"]
            
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Institute name created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(inst_name.id),
                    "code": code
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
        
class GenderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        data = request.data
        serializer = GenderSerializer(data=data)
        if serializer.is_valid():
            gender = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Gender created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(gender.id)
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            genders = Gender.objects.all()
            serializer = GenderViewSerializer(genders, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Gender retrieve successful",
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

class MembershipStatusChoiceView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
    
    def post(self, request):
        data = request.data
        serializer = MembershipStatusChoiceSerializer(data=data)
        if serializer.is_valid():
            membership_status = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Membership status created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(membership_status.id)
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        try:
            membership_status = MembershipStatusChoice.objects.all()
            serializer = MembershipStatusChoiceViewSerializer(membership_status, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Membership status retrieve successful",
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

class MaritalStatusChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
    
    def post(self, request):
        data = request.data
        serializer = MaritalStatusChoiceSerializer(data=data)
        if serializer.is_valid():
            marital_status = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Marital status created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(marital_status.id)
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            marital_status = MaritalStatusChoice.objects.all()
            serializer = MaritalStatusChoiceViewSerializer(marital_status, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Marital status retrieve successful",
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

class EmploymentTypeChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
    def post(self, request):
        data = request.data
        serializer = EmploymentTypeChoiceSerializer(data=data)
        if serializer.is_valid():
            employment_type = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Employment type created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(employment_type.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request):
        try:
            employment_type = EmploymentTypeChoice.objects.all()
            serializer = EmploymentTypeChoiceViewSerializer(employment_type, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Employment type retrieve successful",
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
    
class EmailTypeChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
    
    def post(self, request):
        data = request.data
        serializer = EmailTypeChoiceSerializer(data=data)
        if serializer.is_valid():
            email_type = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Email type created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(email_type.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            email_type = EmailTypeChoice.objects.all()
            serializer = EmailTypeChoiceViewSerializer(email_type, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Email type retrieve successful",
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

class ContactTypeChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
        
    def post(self, request):
        data = request.data
        serializer = ContactTypeChoiceSerializer(data=data)
        if serializer.is_valid():
            contact_type = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Contact type created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(contact_type.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
      
    def get(self, request):
        try:
            contact_type = ContactTypeChoice.objects.all()
            serializer = ContactTypeChoiceViewSerializer(contact_type, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Contact type retrieve successful",
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
            
    
class AddressTypeChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
        
    def post(self, request):
        data = request.data
        serializer = AddressTypeChoiceSerializer(data=data)
        if serializer.is_valid():
            address_type = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Address type created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(address_type.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            address_type = AddressTypeChoice.objects.all()
            serializer = AddressTypeChoiceViewSerializer(address_type, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Address type retrieve successful",
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
    

class DocumentTypeChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
    
    def post(self, request):
        data = request.data
        serializer = DocumentTypeChoiceSerializer(data=data)
        if serializer.is_valid():
            document_type = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Document type created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(document_type.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            document_type = DocumentTypeChoice.objects.all()
            serializer = DocumentTypeChoiceViewSerializer(document_type, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Document type retrieve successful",
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


class SpouseStatusChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
            
    def post(self, request):
        data = request.data
        serializer = SpouseStatusChoiceSerializer(data=data)
        if serializer.is_valid():
            spouse_status = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Spouse status created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(spouse_status.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            spouse_status = SpouseStatusChoice.objects.all()
            serializer = SpouseStatusChoiceViewSerializer(spouse_status, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Spouse status retrieve successful",
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
               
        
        



class DescendantRelationChoiceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        else:
            return [IsAuthenticated()]
    
    def post(self, request):
        data = request.data
        serializer = DescendantRelationChoiceSerializer(data=data)
        if serializer.is_valid():
            descendant_relation = serializer.save()
            name = serializer.validated_data["name"]

            return Response({
                "code": status.HTTP_200_OK,
                "message": "Descendant relation created successfully",
                "status": "success",
                "data": {
                    "name": name,
                    "id": str(descendant_relation.id)
                }
            })

        else:
            return Response({
                "code": 400,
                "status": "failed",
                "message": "Invalid request",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        try:
            descendant_relation = DescendantRelationChoice.objects.all()
            serializer = DescendantRelationChoiceViewSerializer(descendant_relation, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "message": "Descendant relation retrieve successful",
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

    
