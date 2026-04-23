from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from admin_api.permissions import IsAdmin
from workouts.models import Workout,WorkoutCategory
from workouts.serializers.admin import AdminWorkoutSerializer,AdminWorkoutCategorySerializer
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404



class AdminWorkoutCategoryListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = WorkoutCategory.objects.all().order_by("name")

        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminWorkoutCategorySerializer(page, many=True)
        

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AdminWorkoutCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response(
            AdminWorkoutCategorySerializer(category).data,
            status=status.HTTP_201_CREATED
        )

class AdminWorkoutCategoryDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        category = get_object_or_404(WorkoutCategory, pk=pk)
        serializer = AdminWorkoutCategorySerializer(
            category, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        category = get_object_or_404(WorkoutCategory, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AdminWorkoutListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # this is lazy only run sql when sliced
        queryset = Workout.objects.all().order_by("-created_at")
        # return only 10 records in 1 page
        paginator = PageNumberPagination()
        paginator.page_size = 10
        # sliced into 10 records
        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminWorkoutSerializer(page, many=True)
        

        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        serializer = AdminWorkoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  
        workout = serializer.save()
                
        
        return Response(
            AdminWorkoutSerializer(workout).data,
            status=status.HTTP_201_CREATED
        )
        
class AdminWorkoutDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        serializer = AdminWorkoutSerializer(workout)
        return Response(serializer.data)

    def patch(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        serializer = AdminWorkoutSerializer(
            workout,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        workout.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    