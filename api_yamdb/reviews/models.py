from django.db import models
from django.core.validators import validate_slug


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
    

class Genre (models.Model):
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