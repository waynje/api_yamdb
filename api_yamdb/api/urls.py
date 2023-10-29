from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    UserCreateViewSet,
    UserGetTokenViewSet,
)

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', UserCreateViewSet.as_view(), name='signup'),
    path('v1/auth/token/', UserGetTokenViewSet.as_view(), name='token'),
]
