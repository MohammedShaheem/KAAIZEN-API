from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from clients.models import ClientProfile
from clients.serializers.client_profile import ClientProfileSerializer
from clients.permissions import IsClient

class ClientProfileView(APIView):
    permission_Classes = [IsClient]
    
    def get_profile(self,user):
        return ClientProfile.objects.filter(user=user).first()
    
    def get(self,request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response(
                {"detail": "Profile not created yet"},
                status = status.HTTP_404_NOT_FOUND
            )
        serializer = ClientProfileSerializer(profile)
        return Response(serializer.data)
    
    def post(self,request):
        if self.get_profile(request.user):
            return Response(
                {"detail":"Profile already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            serializer = ClientProfileSerializer(
                data = request.data,
                context = {"request":request}
            )
            
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
    def patch(self,request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response(
                {"detail":"Profile not created yet"},
                status=status.HTTP_404_NOT_FOUND
            )
            
            serializer = ClientProfileSerializer(
                profile,
                data=request.data,
                partial=True,
                context={"request":request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data)
            
            