from rest_framework import serializers
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError

from trainers.models import TrainerProfile
from trainers.choices import Skill
from trainers.services.trainer_availability import TrainerAvailabilityService
import logging
logger = logging.getLogger(__name__)

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

        try:
            with transaction.atomic():
                trainer = TrainerProfile.objects.create(
                    user=user,
                    is_verified=False,
                    **validated_data
                )
                logger.info(
                    "creating availability for trainer=%s shift=%s",
                    trainer.id,
                    trainer.shift_type
                )

                TrainerAvailabilityService.create_from_shift(
                    trainer_profile=trainer,
                    shift_type=trainer.shift_type
                )

                return trainer

        except ValidationError:
            raise

        except IntegrityError as e:
            logger.exception(
                "Integrity error during trainer onboarding for user=%s",
                user.id
            )
            raise ValidationError(
                "Trainer profile already exists or data conflict occurred."
            ) from e

        except Exception as e:
            logger.exception(
                "Unexpected error during trainer onboarding for user=%s",
                user.id
            )
            raise ValidationError(
                "Unexpected error occurred while onboarding trainer."
            ) from e
        
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance