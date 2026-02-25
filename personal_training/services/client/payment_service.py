import stripe
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from django.db import transaction
from rest_framework.exceptions import ValidationError

from personal_training.models import TrainingPlan, ClientPlan
from clients.models import ClientProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:

    @staticmethod
    def create_checkout_session(client, plan: TrainingPlan):
        if not plan.stripe_price_id:
            raise ValidationError("Stripe price not configured for this plan.")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",  
            line_items=[{
                "price": plan.stripe_price_id,
                "quantity": 1,
            }],
            metadata={
                "client_id": str(client.id),
                "plan_id": str(plan.id),
            },
            success_url=f"{settings.FRONTEND_URL}/payment-success",
            cancel_url=f"{settings.FRONTEND_URL}/payment-cancel",
        )

        return session

    @staticmethod
    @transaction.atomic
    def handle_successful_payment(session):
        print("this is working from handle successfull payment from payment service")
        client_id = session["metadata"]["client_id"]
        plan_id = session["metadata"]["plan_id"]

        client = ClientProfile.objects.get(id=client_id)
        plan = TrainingPlan.objects.get(id=plan_id)

        # deactivating old plans
        ClientPlan.objects.filter(
            client=client,
            is_active=True
        ).update(is_active=False)

        client_plan = ClientPlan.objects.create(
            client=client,
            plan=plan,
            stripe_checkout_session_id=session["id"],
            status="paid",
            start_date=None,
            end_date=None,
            is_active=False,  
        )

        return client_plan