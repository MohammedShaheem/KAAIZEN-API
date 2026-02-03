from rest_framework import serializers
from trainers.models import TrainerProfile
from trainers.choices import Skill
from trainers.services.trainer_availability import TrainerAvailabilityService


class TrainerProfileSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(
        child=serializers.ChoiceField(choices=Skill.choices),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = TrainerProfile
        exclude = ['user']
        read_only_fields = (
            'created_at',
            'updated_at',
        )

    def validate_skills(self, value):
        # ensuring no duplicates
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate skills are not allowed.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user

        if user.role != "trainer":
            raise serializers.ValidationError(
                "Only trainers can create a trainer profile."
            )

        if TrainerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                "Trainer profile already exists."
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user

        trainer = TrainerProfile.objects.create(
            user=user,
            is_verified=False,
            **validated_data
        )

        TrainerAvailabilityService.set_availability_from_shift(
            trainer=trainer,
            shift_type=trainer.shift_type
        )
        return trainer

        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance