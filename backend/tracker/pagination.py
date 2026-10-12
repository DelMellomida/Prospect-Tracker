from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination


class RecordPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    allowed_page_sizes = [10, 20, 50, 100]

    def get_page_size(self, request):
        page_size = super().get_page_size(request)
        if page_size not in self.allowed_page_sizes:
            raise ValidationError(
                f'Invalid page size. Allowed values are: {self.allowed_page_sizes}'
            )
        return page_size

    def paginate_queryset(self, queryset, request, view=None):
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound as exc:
            raise ValidationError(str(exc))
