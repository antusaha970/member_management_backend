import django_filters
from ..models import *
from django.db.models import Q
import pycountry

country_code = [country.name
                for country in pycountry.countries]


class MemberFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        lookup_expr='icontains')  # Case-insensitive search
    date_of_birth = django_filters.DateFilter()
    blood_group = django_filters.CharFilter(
        lookup_expr='icontains')
    nationality = django_filters.CharFilter(
        lookup_expr='icontains')
    # ForeignKey filters (exact match)
    gender = django_filters.ModelChoiceFilter(
        queryset=Gender.objects.all(), to_field_name="name")
    membership_type = django_filters.ModelChoiceFilter(
        queryset=MembershipType.objects.all(), to_field_name="name")
    institute_name = django_filters.ModelChoiceFilter(
        queryset=InstituteName.objects.all(), to_field_name="name")
    membership_status = django_filters.ModelChoiceFilter(
        queryset=MembershipStatusChoice.objects.all(), to_field_name="name")
    marital_status = django_filters.ModelChoiceFilter(
        queryset=MaritalStatusChoice.objects.all(), to_field_name="name")

    class Meta:
        model = Member
        fields = [
            'first_name', 'date_of_birth', 'blood_group', 'nationality',
            'gender', 'membership_type', 'institute_name', 'membership_status', 'marital_status'
        ]
