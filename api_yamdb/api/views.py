from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
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
from rest_framework.response import Response

from .filters import TitlesFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminModeratorAuthorOrReadOnly,
    IsAdminOrReadOnly,
    AdminOnly,
)
from .serializers import (
    CommentSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleGETSerializer,
    TitleNOTSAFESerliazer,
    ReviewSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserGetTokenSerializer,

)
from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
)


User = get_user_model()


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
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
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


class ReviewViewSet(ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly, )

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class UserCreateViewSet(APIView):

    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = get_object_or_404(User, username=request.data.get('username'))
        confirmation_code = default_token_generator.make_token(user)

        subject = 'YaMDB'
        message = 'Ваш секретный код - ' + confirmation_code

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email, ],
            fail_silently=False,
        )

        return Response(
            {'username': user.username, 'email': user.email},
            status=status.HTTP_200_OK
        )


class UserGetTokenViewSet(APIView):

    permission_classes = (AllowAny,)
    serializer_class = UserGetTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            user = get_object_or_404(User, username=username)
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
        return Response({
            'token': token
        }, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):

    permission_classes = (AdminOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
