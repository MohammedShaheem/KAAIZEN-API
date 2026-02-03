from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from trainers.models import TrainerProfile
from trainers.serializers.trainer_profile import TrainerProfileSerializer
from trainers.permissions import IsTrainer


class TrainerProfileView(APIView):
    permission_classes = [IsTrainer]

    def get_object(self, user):
        return TrainerProfile.objects.filter(user=user).first()

    def get(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response(
                {"detail": "Trainer profile not created yet."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TrainerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if self.get_object(request.user):
            return Response(
                {"detail": "Trainer profile already exists."},
                status=status.HTTP_409_CONFLICT
            )

        serializer = TrainerProfileSerializer(
            data=request.data,
            context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as exc:
            return Response(
                exc.detail,
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError:
            return Response(
                {"detail": "Profile creation failed due to a data conflict."},
                status=status.HTTP_409_CONFLICT
            )
        except Exception:
            return Response(
                {"detail": "Something went wrong while creating profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        profile = self.get_object(request.user)
        if not profile:
            return Response(
                {"detail": "Trainer profile not created yet."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TrainerProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as exc:
            return Response(
                exc.detail,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Something went wrong while updating profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(serializer.data, status=status.HTTP_200_OK)