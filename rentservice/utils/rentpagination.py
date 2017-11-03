from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    def get_paginated_response(self, data, code="0000", msg="Succ"):
        return Response({
            "data": {
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.count,
                'results': data,
                'limit': self.limit,
                'offset': self.offset
            },
            "code": code,
            "message": msg
        })