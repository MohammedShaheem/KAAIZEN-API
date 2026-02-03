from django.db import transaction
from django.core.exceptions import ValidationError

from trainers.models import TrainerAvailability
from trainers.constants import SHIFT_HOURS


class TrainerAvailabilityService:
    @staticmethod
    @transaction.atomic
    def create_from_shift(trainer_profile, shift_type: str):
        """
        create availability slots based on shift_type
        """

        if shift_type not in SHIFT_HOURS:
            raise ValidationError("Invalid shift type selected.")

        TrainerAvailability.objects.filter(trainer=trainer_profile).delete()

        slots = SHIFT_HOURS[shift_type]

        availabilities = []
        for start_time, end_time in slots:
            availabilities.append(
                TrainerAvailability(
                    trainer=trainer_profile,
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        TrainerAvailability.objects.bulk_create(availabilities)

        return availabilities
