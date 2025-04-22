# filters.py
import django_filters
from .models import Facility

class FacilityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    usages_fee__lt = django_filters.NumberFilter(field_name='usages_fee', lookup_expr='lte')
    usages_fee__gt = django_filters.NumberFilter(field_name='usages_fee', lookup_expr='gte')
    usages_roles = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Facility
        fields = ['name', 'usages_fee__lt', 'usages_fee__gt', 'usages_roles']
