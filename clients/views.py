from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.MealAllocationSerializer import MealAllocationSerializer
from .models import MealAllocation
from clients.models import ClientProfile
from clients.serializers.client_profile import ClientProfileSerializer
from clients.permissions import IsClient
import logging

logger = logging.getLogger(__name__)



class ClientProfileView(APIView):
    permission_classes = [IsClient]

    def get_profile(self, user):
        return ClientProfile.objects.filter(user=user).first()

    def get(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response(
                {"detail": "Profile not created yet"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientProfileSerializer(profile)
        print("data from profile get:",serializer.data)
        
        return Response(serializer.data)

    def post(self, request):
        logger.info("from post of client profile view")
        if self.get_profile(request.user):
            return Response(
                {"detail": "Profile already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ClientProfileSerializer(
            data=request.data,
            context={"request": request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def patch(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response(
                {"detail": "Profile not created yet"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    

class MealAllocationsView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        profile = ClientProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"detail": "Profile not created yet"}, status=status.HTTP_404_NOT_FOUND)
        
        allocations = profile.meal_allocations.all()
        serializer = MealAllocationSerializer(allocations, many=True)
        return Response(serializer.data)

    def patch(self, request):
        profile = ClientProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"detail": "Profile not created yet"}, status=status.HTTP_404_NOT_FOUND)
        
        
        meal_type = request.data.get('meal_type')
        if not meal_type:
            return Response({"detail": "Provide 'meal_type'"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            allocation = MealAllocation.objects.get(profile=profile, meal_type=meal_type)
        except MealAllocation.DoesNotExist:
            return Response({"detail": f"No allocation for {meal_type}"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MealAllocationSerializer(
            allocation,
            data=request.data,
            partial=True,
            context={'profile': profile}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
             
        return Response(serializer.data, status=status.HTTP_200_OK)