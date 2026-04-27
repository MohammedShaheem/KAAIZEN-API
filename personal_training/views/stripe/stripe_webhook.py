import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from personal_training.services.client.payment_service import PaymentService

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.webhook_secret = settings.STRIPE_WEBHOOK_SECRET 

"""
disabling csrf protection for this external service.
taking the raw json data and the signature sent by stripe.
signature verification with the webhook secret key stored in the settings.

"""
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event["type"]

    if event_type == "checkout.session.completed":
        
        session = event["data"]["object"]
       
        if session:
            PaymentService.handle_successful_payment(session)

    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]

        session = stripe.checkout.Session.list(
            subscription=invoice["subscription"],
            limit=1
        ).data[0]

        PaymentService.handle_successful_payment(session)

    return HttpResponse(status=200)



