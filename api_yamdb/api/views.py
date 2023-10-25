from http import HTTPStatus
from rest_framework import viewsets
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    
)

from .serializers import(
    CategorySerializer,
    GenreSerializer,
    TitleGETSerializer,
    TitleNOTSAFESerliazer
)
from reviews.models import(
    Category,
    Genre,
    Title
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


class TitleViewSet(viewsets.ModelViewSet):
    
    queryset = Title.objects.all()
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'DELETE']:
            return TitleGETSerializer
        return TitleNOTSAFESerliazer
    