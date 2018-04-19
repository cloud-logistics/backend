from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class ComplexPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, count, view=None):
        self.count = count
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        # return list(queryset[self.offset:self.offset + self.limit])

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
