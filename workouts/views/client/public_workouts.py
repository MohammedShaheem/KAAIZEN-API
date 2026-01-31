from rest_framework.generics import ListAPIView,RetrieveAPIView
from workouts.models import WorkoutCategory
from workouts.serializers.client import ClientWorkoutCategorySerializer,ClientWorkoutSerializer
from .client_base import ClientBaseAPIView
from django.shortcuts import get_object_or_404
from workouts.models import Workout,WorkoutCategory
import logging

logger = logging.getLogger(__name__)


class ClientWorkoutCategoryListView(ClientBaseAPIView, ListAPIView):
    serializer_class = ClientWorkoutCategorySerializer
    queryset = WorkoutCategory.objects.all().order_by("name")



class ClientWorkoutListByCategoryView(ClientBaseAPIView, ListAPIView):
    serializer_class = ClientWorkoutSerializer

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        category = get_object_or_404(WorkoutCategory, id=category_id)

        return (
            Workout.objects
            .filter(category=category)
            .order_by("created_at")
        )
        
class ClientWorkoutDetailView(ClientBaseAPIView, RetrieveAPIView):
    serializer_class = ClientWorkoutSerializer

    def get_queryset(self):
        return Workout.objects.all()