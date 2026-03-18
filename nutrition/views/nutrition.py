from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import MealEntry
from ..serializers.MealEntry import MealEntrySerializer
from django.db.models import Sum


class MealEntryCreateView(APIView):
    def post(self, request):
        print("mealentrycreatepostentering here")
        print("from meal entry create view",request.data.get("time_eaten"))
        serializer = MealEntrySerializer(
            data=request.data,
            context={"request": request} 
        )
        if not serializer.is_valid():
            print("SERIALIZER ERRORS:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MealEntryListByDateView(APIView):
    def get(self, request, date):
        entries = MealEntry.objects.filter(
            user=request.user,
            date_eaten=date
        )

        serializer = MealEntrySerializer(entries, many=True)
        
        return Response(serializer.data)


class DailyNutritionSummaryView(APIView):
    def get(self, request, date):
        entries = MealEntry.objects.filter(
            user=request.user,
            date_eaten=date
        )

        summary = entries.aggregate(
            total_calories=Sum("total_calories"),
            protein=Sum("protein_grams"),
            carbs=Sum("carbs_grams"),
            fat=Sum("fat_grams"),
        )
        
        return Response({
            # "date": date,
            "summary": summary
        })
