from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status


class MembershipTypeView(APIView):
    def post(self,request):
        data = request.data
        serializer=MembershipTypeSerializer(data=data)
        
        if serializer.is_valid():
            mem_type=serializer.save()
            name=serializer.validated_data["name"]
            return Response({
                "name":name,
                "id": str(mem_type.id)
            },status=status.HTTP_201_CREATED)
            
        else:
            return Response({
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)
            

class InstituteNameView(APIView):
    def post(self,request):
        data = request.data
        serializer=InstituteNameSerializer(data=data)
        
        if serializer.is_valid():
            inst_name=serializer.save()
            name=serializer.validated_data["name"]
            return Response({
                "name":name,
                "id": str(inst_name.id)
            },status=status.HTTP_201_CREATED)
            
        else:
            return Response({
                "errors":serializer.errors
            },status=status.HTTP_400_BAD_REQUEST)