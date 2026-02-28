from rest_framework import serializers


class AdminSettlementSerializer(serializers.Serializer):
    settlement_date = serializers.DateField(required=False)