from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers.SleepTracking import DailySleepSerializer

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
