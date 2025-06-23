# filters.py

import django_filters
from .models import EmailList

class EmailListFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains')
    is_subscribed = django_filters.BooleanFilter()
    group = django_filters.NumberFilter(field_name='group')
    group_name = django_filters.CharFilter(field_name='group__name', lookup_expr='icontains')

    class Meta:
        model = EmailList
        fields = ['email', 'is_subscribed', 'group', 'group_name']
