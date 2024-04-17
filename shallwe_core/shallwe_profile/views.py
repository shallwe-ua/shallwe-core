import copy

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shallwe_util.views import MultiPartWithNestedToJSONParser, validate_received_data_structure, UnexpectedFieldError
from .serializers import UserProfileWithParametersCreateUpdateSerializer, UserProfileVisibilityUpdateSerializer
from .serializers.profile import UserProfileWithParametersReadSerializer


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartWithNestedToJSONParser]

    serializer_post, serializer_patch = [UserProfileWithParametersCreateUpdateSerializer] * 2
    serializer_get = UserProfileWithParametersReadSerializer

    def _clean_list_values(self, jsonified_data):
        """Needed for converting single values to lists, because multipart does not support sending 1-element lists"""
        data_copy = copy.deepcopy(jsonified_data)

        for param_group_name, should_be_list_param_name in (
            ('rent_preferences', 'locations'),
            ('about', 'other_animals'),
            ('about', 'interests')
        ):
            if param_group := jsonified_data.get(param_group_name):
                param_value = param_group.get(should_be_list_param_name)

                if param_value and not isinstance(param_value, list):
                    data_copy[param_group_name][should_be_list_param_name] = [param_value]

        return data_copy

    def post(self, request):
        if hasattr(request.user, 'profile'):
            return Response({'error': 'This user already has a profile'}, status=status.HTTP_409_CONFLICT)

        try:
            validate_received_data_structure(request.data, self.serializer_post)
        except UnexpectedFieldError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        clean_data = self._clean_list_values(request.data)
        serializer = self.serializer_post(data=clean_data)

        if serializer.is_valid():
            serializer.save(kwargs={'profile': {'user': request.user}})
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({'error': 'This user has no profile to operate with'}, status=status.HTTP_409_CONFLICT)

        if not request.data:
            return Response({
                'error': 'Empty request body. You should specify at least one field to change.'
            }, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_received_data_structure(request.data, self.serializer_post)
        except UnexpectedFieldError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        clean_data = self._clean_list_values(request.data)
        serializer = self.serializer_patch(instance=request.user.profile, data=clean_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({'error': 'This user has no profile to operate with'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_get(instance=request.user.profile)
        profile_data = serializer.data

        return Response(data=profile_data, status=status.HTTP_200_OK)


class ProfileVisibilityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    serializer_patch = UserProfileVisibilityUpdateSerializer

    def patch(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({'error': 'This user has no profile to operate with'}, status=status.HTTP_409_CONFLICT)

        serializer = self.serializer_patch(instance=request.user.profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
