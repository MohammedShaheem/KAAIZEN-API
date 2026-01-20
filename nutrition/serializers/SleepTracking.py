from rest_framework import serializers
from datetime import datetime, timedelta
from ..models import DailySleep

class DailySleepSerializer(serializers.ModelSerializer):
    sleep_time = serializers.TimeField(write_only=True)
    wake_time = serializers.TimeField(write_only=True)

    class Meta:
        model = DailySleep
        fields = [
            "id",
            "sleep_date",
            "sleep_time",
            "wake_time",
            "hours_slept"
        ]
        read_only_fields = ["hours_slept"]

    def create(self, validated_data):
        user = self.context["request"].user

        sleep_date = validated_data["sleep_date"]
        sleep_time = validated_data.pop("sleep_time")
        wake_time = validated_data.pop("wake_time")

        sleep_start = datetime.combine(sleep_date, sleep_time)
        sleep_end = datetime.combine(sleep_date, wake_time)

        # handle overnight sleep (e.g. 11PM → 6AM)
        if sleep_end <= sleep_start:
            sleep_end += timedelta(days=1)

        hours = (sleep_end - sleep_start).total_seconds() / 3600
        hours = round(hours, 2)

        return DailySleep.objects.create(
            user=user,
            sleep_date=sleep_date,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            hours_slept=hours
        )
