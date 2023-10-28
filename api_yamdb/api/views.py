from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import (
    ModelViewSet,
    GenericViewSet
)
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.pagination import PageNumberPagination

from .filters import TitlesFilter
from .permissions import (
    IsAdminOrReadOnly,
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleGETSerializer,
    TitleNOTSAFESerliazer
)
from reviews.models import (
    Category,
    Genre,
    Title
)


class CategoryGenreMixin(
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):

    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreMixin):

    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):

    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):

    # Тут изменить, когда появится модель Review
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('name',)
    filterset_class = TitlesFilter
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.request.method in ['DELETE']:
            return TitleNOTSAFESerliazer
        return TitleGETSerializer

    def perform_create(self, serializer):
        category_slug = self.request.data.get('category')
        category = get_object_or_404(Category, slug=category_slug)

        genre_slugs = self.request.data.getlist('genre')
        genres = Genre.objects.filter(slug__in=genre_slugs)

        serializer.save(category=category, genre=genres)

    def perform_update(self, serializer):
        self.perform_create(serializer)
