from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from trainers.models import TrainerProfile
from trainers.serializers.trainer_profile import TrainerProfileSerializer
from trainers.permissions import IsTrainer

class TrainerProfileView(APIView):
    permission_classes = [IsTrainer]

    def get_object(self, user):
        try:
            return TrainerProfile.objects.get(user=user)
        except TrainerProfile.DoesNotExist:
            return None

    def get(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response(
                {'detail': 'Profile not created yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TrainerProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        if self.get_object(request.user):
            return Response(
                {'detail': 'Profile already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = TrainerProfileSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            print("SERIALIZER ERRORS:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response(
                {'detail': 'Profile not created yet.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TrainerProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)