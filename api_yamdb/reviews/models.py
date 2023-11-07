import datetime

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.forms import ValidationError

from user.models import User


def year_validator(value):
    if value > datetime.datetime.now().year:
        raise ValidationError("Год выпуска не может быть больше текущего!")


def validate_score(value):
    if 0 < value > 10:
        raise ValidationError(
            ("Оценка должна быть от 1 до 10"),
            params={"value": value},
        )


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        unique=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=75,
        verbose_name="Название",
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        unique=True,
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
    )
    year = models.PositiveIntegerField(
        validators=[year_validator],
        verbose_name="Год выпуска",
    )
    description = models.TextField(verbose_name="Описание")
    genre = models.ManyToManyField(
        Genre, through="GenreTitle", related_name="titles", verbose_name="Жанр"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        related_name="titles",
        null=True,
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = (
            "-year",
            "name",
        )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name="Жанр",
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="Произведение",
    )

    class Meta:
        verbose_name = "Жанр и произведение"
        verbose_name_plural = "Жанры и произведения"
        ordering = ("id",)

    def __str__(self):
        return f"{self.title} входит в жанр {self.genre}"


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        related_name="reviews",
        on_delete=models.CASCADE,
        verbose_name="Произведение",
    )
    text = models.TextField(verbose_name="Текст отзыва")
    author = models.ForeignKey(
        User,
        related_name="reviews",
        on_delete=models.CASCADE,
        verbose_name="Автор отзыва",
    )
    score = models.IntegerField(
        verbose_name="Оценка от 1 до 10",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = (
            models.UniqueConstraint(
                fields=("title", "author"), name="unique_review"
            ),
        )

    def __str__(self):
        return f"{self.text}"


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Отзыв",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    text = models.TextField(verbose_name="Текст комментария")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.text}"
