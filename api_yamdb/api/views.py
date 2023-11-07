from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status, views
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.decorators import action
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
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
    AdminOnly,
)
from .serializers import (
    CommentSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleGetSerializer,
    TitleWriteSerliazer,
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


class TitleReviewCommentMixin(ModelViewSet):
    http_method_names = ["get", "post", "delete", "patch"]


class CategoryGenreMixin(
    ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet
):
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
    queryset = Genre.objects.all().order_by("name")
    serializer_class = GenreSerializer


class TitleViewSet(TitleReviewCommentMixin):
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ("name",)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleGetSerializer
        return TitleWriteSerliazer


class ReviewViewSet(TitleReviewCommentMixin):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()


class CommentViewSet(TitleReviewCommentMixin):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        return review.comments.all()

    # def perform_create(self, serializer):
    #    title_id = self.kwargs.get('title_id')
    #    title = get_object_or_404(Title, id=title_id)
    #    serializer.save(author=self.request.user, title=title)

    # def perform_create(self, serializer):
    #     title_id = self.kwargs.get('title_id')
    #     title = get_object_or_404(Title, id=title_id)
    #     serializer.save(author=self.request.user, title=title)


class UserCreateViewSet(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = get_object_or_404(User, username=request.data.get("username"))
        confirmation_code = default_token_generator.make_token(user)

        subject = "YaMDB"
        message = "Ваш секретный код - " + confirmation_code

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [
                user.email,
            ],
            fail_silently=False,
        )

        return Response(
            {"username": user.username, "email": user.email},
            status=status.HTTP_200_OK,
        )


class UserGetTokenViewSet(views.APIView):
    queryset = User.objects.all()
    serializer_class = UserGetTokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserGetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        confirmation_code = serializer.validated_data.get("confirmation_code")
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {"confirmation_code": "Код подтверждения невалиден"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {"token": str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False,
        methods=["get", "patch", "delete"],
        url_path=r"(?P<username>[\w.@+-]+)",
        url_name="user",
    )
    def user(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == "PATCH":
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
