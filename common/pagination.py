from rest_framework.pagination import CursorPagination


class MyCursorPagination(CursorPagination):
    page_size = 2
    max_page_size = 100
    ordering = "-id"
    page_size_query_param = "page_size"
    page_query_param = "cursor"


def paginate_queryset(queryset, request, view, serializer_class):
    pagination = MyCursorPagination()

    paginated_queryset = pagination.paginate_queryset(
        queryset,
        request,
        view=view
    )

    serializer = serializer_class(
        paginated_queryset,
        many=True
    )

    return {
        "total": queryset.count(),
        "next": pagination.get_next_link(),
        "previous": pagination.get_previous_link(),
        "data": serializer.data,
    }
