from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import(
    SearchFilter,
    OrderingFilter,
)
from rest_framework.pagination import PageNumberPagination

from .filters import TitlesFilter
from .permissions import(
    IsAdminOrReadOnly,
)
from .serializers import(
    CategorySerializer,
    GenreSerializer,
    TitleGETSerializer,
    TitleNOTSAFESerliazer,
    ReviewSerializer
)
from reviews.models import(
    Category,
    Genre,
    Review,
    Title
)


class CategoryGenreMixin(ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    


class CategoryViewSet(CategoryGenreMixin):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class GenreViewSet(CategoryGenreMixin):
    
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    
    queryset = Title.objects.all() ### Тут нужно будет изменить, когда появится модель Review
    permission_classes = IsAdminOrReadOnly
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('name',)
    filterset_class = TitlesFilter
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'DELETE']:
            return TitleGETSerializer
        return TitleNOTSAFESerliazer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)
