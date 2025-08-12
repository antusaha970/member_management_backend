# products/filters.py
import django_filters
from .. models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='brand__name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['name', 'category', 'brand']
