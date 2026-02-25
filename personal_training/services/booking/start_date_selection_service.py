from django.core.exceptions import ValidationError
from personal_training.utils.client_booking_cache import get_booking_data,save_booking_field


class StartDateSelectionService:

    @staticmethod
    def select_start_date(client_id, start_date):

        booking_data = get_booking_data(client_id)

        if not booking_data:
            raise ValidationError("Booking session expired.")

        if "trainer_id" not in booking_data:
            raise ValidationError("Please select trainer first.")

        save_booking_field(
            client_id=client_id,
            field="start_date",
            value=str(start_date)
        )

        return True