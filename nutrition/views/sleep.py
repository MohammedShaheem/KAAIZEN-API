from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers.SleepTracking import DailySleepSerializer
from django.utils.timezone import now
from django.db.models import Sum, Avg
from datetime import timedelta
from ..models import DailySleep

class DailySleepCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DailySleepSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            sleep = serializer.save()
            return Response(
                {
                    "message": "Sleep logged successfully",
                    "hours_slept": sleep.hours_slept
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeeklySleepReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()
        start_date = today - timedelta(days=6)

        sleeps = DailySleep.objects.filter(
            user=user,
            sleep_date__range=[start_date, today]
        )

        # Map date -> hours
        sleep_map = {
            sleep.sleep_date: float(sleep.hours_slept)
            for sleep in sleeps
        }

        data = []
        total_sleep = 0

        for i in range(7):
            day = start_date + timedelta(days=i)
            hours = sleep_map.get(day, 0)

            data.append({
                "date": day.isoformat(),
                "hours": round(hours, 2)
            })

            total_sleep += hours

        average_sleep = round(total_sleep / 7, 2)

        return Response({
            "average_sleep": average_sleep,
            "total_sleep": round(total_sleep, 2),
            "data": data
        })