from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data, code="0000", msg="Succ"):

        return Response({
            "data": {
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'results': data,
                'num_pages': self.page.paginator.num_pages
            },
            "code": code,
            "message": msg
        })