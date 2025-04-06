from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from .models import RestaurantCuisineCategory, RestaurantCategory, Restaurant, RestaurantItemCategory, RestaurantItem
import pdb


class RestaurantCuisineCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantCuisineCategorySerializer(
                data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Cuisine category was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            cuisines = RestaurantCuisineCategory.objects.filter(is_active=True)
            serializer = serializers.RestaurantCuisineCategorySerializer(
                cuisines, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "viewing all available cuisines",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantCategorySerializer(
                data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Category was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            categories = RestaurantCategory.objects.filter(is_active=True)
            serializer = serializers.RestaurantCategorySerializer(
                categories, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "viewing all available categories",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            data = Restaurant.objects.filter(is_active=True)
            serializer = serializers.RestaurantViewSerializer(data, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "Viewing all available restaurant",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            })

    def post(self, request):
        try:
            serializer = serializers.RestaurantSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Restaurant was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantItemCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantItemCategorySerializer(
                data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Item category was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            cuisines = RestaurantItemCategory.objects.filter(is_active=True)
            serializer = serializers.RestaurantItemCategorySerializer(
                cuisines, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "viewing all available item categories",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantItemView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            restaurant_id = request.query_params.get("restaurant")
            if restaurant_id:
                if not Restaurant.objects.filter(id=restaurant_id).exists():
                    return Response({
                        "code": 400,
                        "status": "bad request",
                        "message": "Something want wrong",
                        "errors": {
                            "restaurant_id": ["Not restaurant exist with this id"]
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    items = RestaurantItem.objects.filter(
                        restaurant__id=restaurant_id)
                    serializer = serializers.RestaurantItemForViewSerializer(
                        items, many=True)
                    return Response({
                        "code": 200,
                        "status": "success",
                        "message": "Viewing all restaurant items",
                        "data": serializer.data
                    })
            else:
                return Response({
                    "code": 400,
                    "status": "bad request",
                    "message": "Something want wrong",
                    "errors": {
                        "query_param": ["Missing required query parameter restaurant"]
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.RestaurantItemSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Successfully created restaurant item",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "success",
                    "message": "Something went wrong",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
