from rest_framework import serializers
from personal_training.models import ClientPlan
from personal_training.models import TrainingPlan




class ClientSubscriptionSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField(source="client.id", read_only=True)
    client_name = serializers.CharField(
        source="client.user.get_full_name",
        read_only=True
    )
    client_email = serializers.EmailField(
        source="client.user.email",
        read_only=True
    )

    class Meta:
        model = ClientPlan
        fields = [
            "client_id",
            "client_name",
            "client_email",
            "start_date",
            "end_date",
            "is_active",
        ]
class TrainingPlanDetailSerializer(serializers.ModelSerializer):
    active_subscriptions = serializers.SerializerMethodField()
    clients = ClientSubscriptionSerializer(
        source="subscriptions",
        many=True,
        read_only=True
    )
 
    class Meta:
        model = TrainingPlan
        fields = [
            "id",
            "name",
            "duration_days",
            "price",
            "description",
            "is_active",
            "active_subscriptions",
            "clients",
            "created_at",
            "updated_at",
        ]

    def get_active_subscriptions(self, obj):
        return obj.subscriptions.filter(is_active=True).count()