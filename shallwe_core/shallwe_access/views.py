from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class GetProfileStatusView(APIView):
    """Returns 403 if not logged in, 404 if has no profile, 200 if logged in and profile has been created"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_200_OK)
