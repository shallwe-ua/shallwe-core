from rest_framework import status
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shallwe_util.views import MultiPartWithNestedToJSONParser, validate_received_data_structure, UnexpectedFieldError
from .models import UserProfile
from .serializers import UserProfileWithParametersSerializer


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartWithNestedToJSONParser]

    serializer_post = UserProfileWithParametersSerializer

    def post(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user):
            return Response({'error': 'This user already has a profile'}, status=status.HTTP_409_CONFLICT)

        try:
            validate_received_data_structure(request.data, self.serializer_post)
        except UnexpectedFieldError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_post(data=request.data, *args, **kwargs)

        if serializer.is_valid():
            serializer.save(kwargs={'profile': {'user': request.user}})
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
