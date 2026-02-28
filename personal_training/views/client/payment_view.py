import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.permissions import IsClient

from personal_training.serializers.client.payment_serializer import CreateCheckoutSerializer
from personal_training.services.client.payment_service import PaymentService

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        print("entering here create shceckout session view")
        serializer = CreateCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = request.user.client_profile
        plan = serializer.validated_data["plan_id"]

        session = PaymentService.create_checkout_session(client, plan)
        

        return Response({
            "checkout_url": session.url
        }, status=status.HTTP_200_OK)