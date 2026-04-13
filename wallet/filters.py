import django_filters
from django.db.models import Q
from wallet.models import WalletTransaction
from users.choices import EntryType, Status


class BaseTransactionFilter(django_filters.FilterSet):
    entry_type = django_filters.ChoiceFilter(choices=EntryType.choices)
    status = django_filters.ChoiceFilter(choices=Status.choices)
    transaction_type = django_filters.CharFilter(lookup_expr="icontains")
    date_from = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    reference_id = django_filters.UUIDFilter(field_name="reference_id")

    class Meta:
        model = WalletTransaction
        fields = [
            "entry_type",
            "status",
            "transaction_type",
            "date_from",
            "date_to",
            "amount_min",
            "amount_max",
            "reference_id",
        ]


class ClientTransactionFilter(BaseTransactionFilter):
    """Filter for client wallet transactions."""
    pass


class TrainerTransactionFilter(BaseTransactionFilter):
    """Filter for trainer wallet transactions."""
    pass