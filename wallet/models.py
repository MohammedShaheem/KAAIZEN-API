from django.db import models
from decimal import Decimal
from core.models import UUIDModel,TimeStampedModel
from users.choices import  EntryType,Status
from users.models import User
# Create your models here.
class Wallet(UUIDModel,TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00")
    )

    currency = models.CharField(max_length=10, default="INR")

    is_active = models.BooleanField(default=True)


    class Meta:
        db_table = "wallets"
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.balance} {self.currency}"
    


class WalletTransaction(UUIDModel,TimeStampedModel):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)

    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices
    )

    transaction_type = models.CharField(
        max_length=50,
    )

    reference_id = models.UUIDField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    description = models.TextField(null=True, blank=True)

    balance_before = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = "wallet_transactions"
        indexes = [
            models.Index(fields=["wallet"]),
            models.Index(fields=["reference_id"]),
            models.Index(fields=["transaction_type"]),
        ]