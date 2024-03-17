import copy

from rest_framework import status
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shallwe_util.views import MultiPartWithNestedToJSONParser, validate_received_data_structure, UnexpectedFieldError
from .serializers import UserProfileWithParametersSerializer


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartWithNestedToJSONParser]

    serializer_post = UserProfileWithParametersSerializer

    def _clean_list_values(self, jsonified_data):
        """Needed for converting single values to lists, because multipart does not support sending 1-element lists"""
        data_copy = copy.deepcopy(jsonified_data)

        for param_group, should_be_list_param in (
            ('rent_preferences', 'locations'),
            ('about', 'other_animals'),
            ('about', 'interests')
        ):
            param_value = jsonified_data.get(param_group).get(should_be_list_param)
            if param_value and not isinstance(param_value, list):
                data_copy[param_group][should_be_list_param] = [param_value]

        return data_copy

    def post(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            return Response({'error': 'This user already has a profile'}, status=status.HTTP_409_CONFLICT)

        try:
            validate_received_data_structure(request.data, self.serializer_post)
        except UnexpectedFieldError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        clean_data = self._clean_list_values(request.data)
        serializer = self.serializer_post(data=clean_data, *args, **kwargs)

        if serializer.is_valid():
            serializer.save(kwargs={'profile': {'user': request.user}})
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
