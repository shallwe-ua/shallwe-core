from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


class SampleAuthenticatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # This endpoint is accessible only for authenticated users.
        # If the request passes authentication, it reaches here.
        user = request.user  # The authenticated user
        return Response({"message": f"Hello, {user.username}! You are authenticated."})


class SampleGeneralView(APIView):

    def get(self, request):
        return Response({"message": f"Hello! Make yourself at home!"})
