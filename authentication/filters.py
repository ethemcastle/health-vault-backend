from django.db.models import Q
from django_filters import FilterSet, CharFilter, OrderingFilter

from authentication.models import User


class UserFilter(FilterSet):
    full_name = CharFilter(method='filter_by_full_name', label="Full Name")
    ordering = OrderingFilter(
        fields=(
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
            ('email', 'email'),
        ),
        field_labels={
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
        }
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'full_name', 'email', 'birthday', 'country_of_birth', 'is_active']

    @staticmethod
    def filter_by_full_name(queryset, name: str, value: str):
        """
        Custom filter to allow filtering by full name.
        """
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )

    @property
    def qs(self):
        request = self.request
        if request is None:
            return User.objects.none()
        parent = super(UserFilter, self).qs
        return parent
