from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    GenreViewSet,
    
)

router = routers.DefaultRouter()
router.register('categories/', CategoryViewSet, basename='categories')
router.register('genres/', GenreViewSet, basename='genres')

urlpatterns = [
    path('', include(router.urls))
]
