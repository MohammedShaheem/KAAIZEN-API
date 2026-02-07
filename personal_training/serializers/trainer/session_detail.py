from rest_framework import serializers
from personal_training.models import TrainingSession, ClientPlan
from clients.models import ClientProfile


class ClientBasicSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            "id",
            "full_name",
            "gender",
            "date_of_birth",
            "email",
        ]


class ClientPlanSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = ClientPlan
        fields = [
            "plan_name",
            "start_date",
            "end_date",
            "sessions_per_week",
            "session_duration_minutes",
            "is_active",
        ]


class TrainerSessionDetailSerializer(serializers.ModelSerializer):
    client = ClientBasicSerializer(read_only=True)
    active_plan = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = [
            "id",
            "session_date",
            "start_time",
            "end_time",
            "status",
            "client",
            "active_plan",
        ]

    def get_active_plan(self, obj):
        plan = (
            ClientPlan.objects
            .filter(client=obj.client, is_active=True)
            .select_related("plan")
            .first()
        )
        return ClientPlanSerializer(plan).data if plan else None
