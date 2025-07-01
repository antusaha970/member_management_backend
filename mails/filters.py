# filters.py

import django_filters
from .models import EmailList, Outbox,STATUS_CHOICES

class EmailListFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains')
    is_subscribed = django_filters.BooleanFilter()
    group = django_filters.NumberFilter(field_name='group')
    group_name = django_filters.CharFilter(field_name='group__name', lookup_expr='icontains')

    class Meta:
        model = EmailList
        fields = ['email', 'is_subscribed', 'group', 'group_name']

class OutboxFilter(django_filters.FilterSet):
    email_address = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)
    is_from_template = django_filters.BooleanFilter()

    class Meta:
        model = Outbox
        fields = ['email_address', 'status', 'is_from_template']