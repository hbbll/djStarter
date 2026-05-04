import django_filters
from apps.account.models import CustomUser


class UserFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()
    is_superuser = django_filters.BooleanFilter()
    locale = django_filters.CharFilter()

    created_at_from = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_to = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "locale",
        ]
