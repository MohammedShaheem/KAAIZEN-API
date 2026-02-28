from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError


def calculate_pricing(amount_total, total_sessions):
        
    total_price = (Decimal(amount_total) / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    if total_sessions <= 0:
        raise ValidationError("Invalid total sessions for pricing calculation.")

    per_session_price = (total_price / total_sessions).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return total_price, per_session_price