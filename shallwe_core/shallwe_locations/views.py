from rest_framework.views import APIView
from rest_framework.response import Response

from .search import search


class LocationSearchView(APIView):

    def get(self, request):
        search_term = request.query_params.get('query', None)

        # Check if search_term is valid
        if search_term is None:
            return Response({'error': 'No search term provided'}, status=400)
        elif len(search_term) < 2 or len(search_term) > 32:
            return Response({'error': 'Search term length should be between 2 and 32 characters'}, status=400)

        result = search(search_term)

        # Check if anything matched
        if result.is_empty():
            return Response({'error': 'No matching locations found'}, status=404)
        else:
            return Response(result.to_dict())
