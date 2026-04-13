import stripe
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from django.db import transaction
from rest_framework.exceptions import ValidationError

from personal_training.models import TrainingPlan, ClientPlan
from clients.models import ClientProfile
from personal_training.utils.calculate_pricing import calculate_pricing

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
        
        
        session_id = session["id"]
        print("Session: ",session_id)
        
        if ClientPlan.objects.filter(
            stripe_checkout_session_id=session_id
            ).exists():
            return

        metadata = session.get("metadata", {})

        client_id = metadata.get("client_id")
        plan_id = metadata.get("plan_id")
        print("clientid:",client_id)
        print("planid:",plan_id)

        if not client_id or not plan_id:
            raise ValidationError("Invalid metadata in Stripe session.")
        
        
        client = ClientProfile.objects.get(id=client_id)
        print("client: ",client)
        plan = TrainingPlan.objects.get(id=plan_id)

        amount_total = session.get("amount_total")

        if amount_total is None:
            raise ValidationError("Stripe session missing amount_total.")
        
        total_sessions = plan.total_sessions
        
        
        total_price, per_session_price = calculate_pricing(
            amount_total,
            total_sessions
        )

        
        
        ClientPlan.objects.filter(
            client=client,
            is_active=True
        ).update(is_active=False)

        client_plan = ClientPlan.objects.create(
            client=client,
            plan=plan,
            stripe_checkout_session_id=session_id,
            stripe_subscription_id=session.get("subscription"),
            status="paid",
            total_price=total_price,
            total_session=total_sessions,
            per_session_price=per_session_price,
            start_date=None,
            end_date=None,
            is_active=False,  
        )
       
        return client_plan