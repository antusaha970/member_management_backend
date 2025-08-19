import django_filters
from member.models import Member


class CreatedAtFilterSet(django_filters.FilterSet):
    created_at = django_filters.DateFilter(
        field_name="created_at", lookup_expr="date")
    created_at_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte")

    class Meta:
        abstract = True


class MemberFilter(CreatedAtFilterSet):
    class Meta(CreatedAtFilterSet.Meta):
        model = Member
        fields = ["created_at", "created_at_after", "created_at_before"]
