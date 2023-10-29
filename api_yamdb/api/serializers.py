from rest_framework import serializers

from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
    year_validator
)
from user.models import User


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

class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким логином уже существует, укажите другой'
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует, укажите другой'
            )
        if data.get('username') == 'me':
            raise serializers.ValidationError('Пожалуйста, используйте другое имя!')
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role'
        )

    @staticmethod
    def validate_username(username):
        if username == 'me':
            raise serializers.ValidationError(
                'Пожалуйста, используйте другое имя!'
            )
        return username


class UserGetTokenSerializer(serializers.Serializer):

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )
