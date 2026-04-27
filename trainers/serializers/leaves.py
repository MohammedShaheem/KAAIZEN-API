from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError  # ← add this

from trainers.models import TrainerLeave
from trainers.services.trainer_leave_service import TrainerLeaveService


class TrainerLeaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainerLeave
        fields = (
            "id",
            "start_date",
            "end_date",
            "reason",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if not start_date or not end_date:
            raise serializers.ValidationError(
                "Start date and end date are required."
            )

        if start_date > end_date:
            raise serializers.ValidationError(
                "End date cannot be earlier than start date."
            )

        return attrs

    def create(self, validated_data):
        trainer = self.context["request"].user.trainer_profile

        try:                                                      
            return TrainerLeaveService.create_leave(
                trainer=trainer,
                start_date=validated_data["start_date"],
                end_date=validated_data["end_date"],
                reason=validated_data.get("reason", "")
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
