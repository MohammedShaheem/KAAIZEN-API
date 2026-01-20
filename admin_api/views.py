from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User
from users.choices import UserRole
from admin_api.permissions import IsAdmin
from rest_framework import status
from django.utils.timezone import now,timedelta
from rest_framework.pagination import PageNumberPagination
from admin_api.serializers.users import AdminClientListSerilalizer,AdminTrainerListSerilalizer,AdminClinetDetailSerialier
from clients.models import ClientProfile
from django.db.models import Q
from trainers.models import TrainerProfile
from admin_api.serializers.trainers import TrainerVerificationListSerializer,TrainerVerificationDetailSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone   
from admin_api.serializers.users import AdminTrainerDetailSerialier


class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self,request):
        last_7_days = now() - timedelta(days=7)
        
        data = {
            "total_users": User.objects.filter(role__in=[UserRole.CLIENT, UserRole.TRAINER]).count(),
            "active_users": User.objects.filter(role__in=[UserRole.CLIENT, UserRole.TRAINER],is_active=True).count(),
            "clients":User.objects.filter(role=UserRole.CLIENT).count(),
            "trainers": User.objects.filter(role=UserRole.TRAINER).count(),
            "new_users":User.objects.filter(
                created_at__gte=last_7_days
            ).count(),
        }
        
        return Response(data)

##################################################################################
class AdminClientListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        queryset = User.objects.filter(
            role=UserRole.CLIENT
        ).order_by("-created_at")
        
        search = request.query_params.get("search")
        
        if search:
            queryset = queryset.filter(email__icontains=search)
            
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        page = paginator.paginate_queryset(queryset,request)
        serializer = AdminClientListSerilalizer(page,many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
class AdminClientDetailsView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self,request,user_id):
        profile = ClientProfile.objects.filter(user=user_id).select_related("user").first()
        
        if not profile:
            return Response(
                {"detail":"Trainer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdminTrainerDetailSerialier(profile)
        return Response(serializer.data)
############################################################################################

class AdminTrainerListView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self,request):
        queryset = User.objects.filter(
            role=UserRole.TRAINER
            ).order_by("-created_at")
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        page = paginator.paginate_queryset(queryset,request)
        serializer = AdminTrainerListSerilalizer(page,many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    
class AdminTrainerDetailsView(APIView):
    permission_classes = [IsAdmin]
    
    def get(self,request,user_id):
        
        profile = TrainerProfile.objects.filter(user=user_id).select_related("user").first()
        
        
        if not profile:
            return Response(
                {"detail":"Client profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdminClinetDetailSerialier(profile)
        return Response(serializer.data)
    
#############################################################################################

class AdminUserStatusView(APIView):
    permission_classes = [IsAdmin]
    
    def patch(self,request,user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(
                {"detail":"User not found"},
                status = status.HTTP_404_NOT_FOUND
            )
        is_active = request.data.get("is_active")
        if is_active is None:
            return Response(
                {"detail":"is_active field is required"},
                status = status.HTTP_400_BAD_REQUEST
            )
            
        user.is_active = bool(is_active)
        user.save(update_fields=['is_active'])
        
        return Response({
            "detail":"User status update",
            "is_active":user.is_active
        })
        
class AdminTrainerStatusView(APIView):
    permission_classes = [IsAdmin]
    
    def patch(self,request,user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(
                {"detail":"User not found"},
                status = status.HTTP_404_NOT_FOUND
            )
        is_active = request.data.get("is_active")
        if is_active is None:
            return Response(
                {"detail":"is_active field is required"},
                status = status.HTTP_400_BAD_REQUEST
            )
            
        user.is_active = bool(is_active)
        user.save(update_fields=['is_active'])
        
        return Response({
            "detail":"User status update",
            "is_active":user.is_active
        })
##################################################################################################

class PendingTrainerVerificationList(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        queryset = TrainerProfile.objects.filter(
            is_verified=False,
            experience_certificate__isnull=False
        ).order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(queryset, request)
        serializer = TrainerVerificationListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

class VerifyTrainerAPIView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        approve = request.data.get("approve")

        profile = get_object_or_404(TrainerProfile, pk=pk)
        user = profile.user

        if approve:
            profile.is_verified = True
            profile.verified_at = timezone.now()
            profile.verified_by = request.user
            profile.save()

            user.is_verified = True
            user.save(update_fields=["is_verified"])
        else:
            profile.is_verified = False
            user.is_verified = False
            user.save(update_fields=["is_verified"])

        return Response({"detail": "Trainer verification updated"})


class TrainerVerificationDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        profile = TrainerProfile.objects.select_related("user").filter(pk=pk).first()

        if not profile:
            return Response(
                {"detail": "Trainer profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TrainerVerificationDetailSerializer(profile)
        return Response(serializer.data)
