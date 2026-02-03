from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCsrfToken(APIView):
    def get(self,request):
        return JsonResponse({"detail":"CSRF cookie set"})