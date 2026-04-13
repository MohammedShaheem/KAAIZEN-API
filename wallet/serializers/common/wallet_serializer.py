from rest_framework import serializers
from wallet.models import WalletTransaction


class WalletSummarySerializer(serializers.Serializer):
    wallet_id = serializers.UUIDField()
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField()
    is_active = serializers.BooleanField()


class TransactionUserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()


class WalletTransactionSerializer(serializers.ModelSerializer):
    from_user = TransactionUserSerializer(read_only=True)
    to_user = TransactionUserSerializer(read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            "id",
            "amount",
            "entry_type",
            "transaction_type",
            "status",
            "reference_id",
            "description",
            "balance_before",
            "balance_after",
            "from_user",
            "to_user",
            "created_at",
        ]
        read_only_fields = fields