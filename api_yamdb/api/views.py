from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

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
    
    queryset = Title.objects.all()
    permission_classes = IsAdminOrReadOnly
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'DELETE']:
            return TitleGETSerializer
        return TitleNOTSAFESerliazer
    