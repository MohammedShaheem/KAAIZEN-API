from rest_framework import serializers


class TrainerSelectionSerializer(serializers.Serializer):
    trainer_id = serializers.UUIDField()
