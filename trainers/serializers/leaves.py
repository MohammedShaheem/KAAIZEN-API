from rest_framework import serializers
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
        request = self.context["request"]
        trainer = request.user.trainer_profile

        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        TrainerLeaveService.validate_leave_limit(
            trainer=trainer,
            start_date=start_date
        )

        TrainerLeaveService.validate_overlapping_leave(
            trainer=trainer,
            start_date=start_date,
            end_date=end_date
        )

        return attrs

    def create(self, validated_data):
        trainer = self.context["request"].user.trainer_profile

        return TrainerLeaveService.create_leave(
            trainer=trainer,
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
            reason=validated_data.get("reason", "")
        )
