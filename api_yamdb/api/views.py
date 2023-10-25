from http import HTTPStatus
from rest_framework import viewsets
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

from .serializers import(
    CategorySerializer,
    GenreSerializer,
)
from reviews.models import(
    Category,
    Genre,
)


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


class GenreViewSet(viewsets.ModelViewSet):
    
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]