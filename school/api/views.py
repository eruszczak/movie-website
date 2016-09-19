from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from school.program.main import get_answer


class GetResponse(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q')
        response = ''
        if query:
            response = get_answer(query)
        response = Response(response, status=status.HTTP_200_OK)
        return response
