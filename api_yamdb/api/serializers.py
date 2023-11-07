import re

from rest_framework import serializers
from django.shortcuts import get_object_or_404

from reviews.models import (
    Comment,
    Category,
    Genre,
    Review,
    Title,
    year_validator,
)
from user.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ("id",)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ("id",)


class TitleGetSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "description",
            "rating",
            "genre",
            "category",
        )
        model = Title


class TitleWriteSerliazer(serializers.ModelSerializer):
    year = serializers.IntegerField(validators=[year_validator])
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    class Meta:
        fields = ("id", "name", "year", "genre", "description", "category")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "text",
            "author",
            "score",
            "pub_date",
        )
        read_only_fields = ("title",)

    def validate(self, data):
        if self.context["request"].method == "POST":
            title_id = self.context["view"].kwargs["title_id"]
            title = get_object_or_404(Title, id=title_id)
            author = self.context["request"].user
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    "Отзыв на это произведение уже есть"
                )
            data["author"] = author
            data["title"] = title
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
        read_only_fields = ("review",)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        review_id = self.context["view"].kwargs["review_id"]
        validated_data["review"] = get_object_or_404(Review, id=review_id)
        return super().create(validated_data)


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ("username", "email")

    def create(self, validated_data):
        email = validated_data.get("email")
        username = validated_data.get("username")
        if User.objects.filter(email=email, username=username).exists():
            return User.objects.filter(email=email, username=username)
        else:
            if (
                User.objects.filter(username=username).exists()
                or User.objects.filter(email=email).exists()
            ):
                raise serializers.ValidationError(
                    {"username": ["Не ваша почта или ник!"]}
                )
        return User.objects.create_user(
            email=email,
            username=username,
            is_active=False,
        )

    def validate_username(self, username):
        if username == "me":
            raise serializers.ValidationError("Недопустимый username!")
        if not re.match(r"^[\w.@+-]+\Z", username):
            raise serializers.ValidationError("Недопустимые символы")
        return username


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    @staticmethod
    def validate_username(username):
        if username == "me":
            raise serializers.ValidationError(
                "Пожалуйста, используйте другое имя!"
            )
        return username


class UserGetTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r"^[\w.@+-]+$", max_length=150, required=True
    )
    confirmation_code = serializers.CharField(max_length=150, required=True)
