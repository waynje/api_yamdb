import datetime
from django.db import models
from django.core.validators import validate_slug
from django.forms import ValidationError


def year_validator(value):
    if value > datetime.datetime.now().year:
        raise ValidationError('Год выпуска не может быть больше текущего!')


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Слаг',
        unique=True,
        validators=[validate_slug]
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=75,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Слаг',
        unique=True,
        validators=[validate_slug]
    )
    
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)
    
    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,
    )
    year = models.PositiveIntegerField(
        validators=[year_validator],
        blank=False,
        null=False,
        verbose_name='Год выпуска',
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='titles',
        null=True
    )
    
    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name',)
    
    def __str__(self):
        return self.name
    

class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    
    class Meta:
        verbose_name = 'Жанр и произведение'
        verbose_name_plural = 'Жанры и произведения'
        ordering = ('id',)
    
    def __str__(self):
        return f'{self.title} входит в жанр {self.genre}'