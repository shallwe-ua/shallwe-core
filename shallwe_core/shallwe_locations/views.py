from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .search import search


class LocationSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_terms_all = request.GET.getlist('query')

        # Check there only one search term
        if len(search_terms_all) != 1:
            return Response({'error': 'Exactly one search term should be provided'}, status=400)

        search_term = search_terms_all[0]

        # Check if search term is valid
        if not search_term:
            return Response({'error': 'Search term is empty'}, status=400)
        elif len(search_term) < 2 or len(search_term) > 32:
            return Response({'error': 'Search term length should be between 2 and 32 characters'}, status=400)

        result = search(search_term)

        # Check if anything matched
        if result.is_empty():
            return Response({'error': 'No matching locations found'}, status=404)
        else:
            return Response(result.to_dict())
