from rest_framework import serializers

from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
    year_validator
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGETSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    category = CategorySerializer(read_only=True)
    
    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'rating',
            'genre',
            'category',
        )
        model = Title


class TitleNOTSAFESerliazer(serializers.ModelSerializer):
    year = serializers.IntegerField(
        validators=[year_validator]
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    
    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'description',
            'category'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Review
