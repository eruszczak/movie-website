from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from school.program.main import get_answer


class test(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q')
        res = ''
        if query:
            res = get_answer(query)
        response = Response(res, status=status.HTTP_200_OK)
        return response
