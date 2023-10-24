from django.shortcuts import render
from rest_framework import viewsets

from .serializers import CategorySerializer
from reviews.models import Category


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
