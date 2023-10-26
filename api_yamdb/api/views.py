from http import HTTPStatus
from rest_framework import viewsets

from .permissions import(
    IsAdminOrReadOnly,
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
    permission_classes = IsAdminOrReadOnly


class GenreViewSet(viewsets.ModelViewSet):
    
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = IsAdminOrReadOnly


class TitleViewSet(viewsets.ModelViewSet):
    
    queryset = Title.objects.all()
    permission_classes = IsAdminOrReadOnly
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'DELETE']:
            return TitleGETSerializer
        return TitleNOTSAFESerliazer
    