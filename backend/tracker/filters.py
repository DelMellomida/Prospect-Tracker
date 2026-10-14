import django_filters
from django.db.models import Q
from django.utils import timezone

from .models import Record


class RecordFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q', label='Search')
    sort_by = django_filters.CharFilter(method='filter_sort_by', label='Sort By')
    follow_up_due = django_filters.BooleanFilter(
        method='filter_follow_up_due',
        label='Follow Up Due',
    )

    class Meta:
        model = Record
        fields = [
            'status',
        ]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(company__icontains=value) |
            Q(source__icontains=value)
        )

    def filter_sort_by(self, queryset, name, value):
        order = self.request.GET.get('order', 'asc')
        if value == 'last_date_contacted':
            if order == 'desc':
                return queryset.order_by('-last_date_contacted')
            return queryset.order_by('last_date_contacted')
        return queryset

    def filter_follow_up_due(self, queryset, name, value):
        if value:
            today = timezone.localdate()
            return queryset.filter(follow_up__follow_up_date__lte=today)
        return queryset
