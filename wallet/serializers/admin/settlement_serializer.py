from rest_framework import serializers


class AdminSettlementSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()