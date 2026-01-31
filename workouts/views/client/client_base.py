from rest_framework.generics import GenericAPIView
from core.permissions import IsClient
from rest_framework.pagination import PageNumberPagination


class ClientPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ClientBaseAPIView(GenericAPIView):
    permission_classes = [IsClient]
    pagination_class = ClientPagination
    
