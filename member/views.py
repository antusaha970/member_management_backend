from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pass
