from django.contrib.auth.models import AbstractUser
from django.db import models

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'


class User(AbstractUser):
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField(
        max_length=254, verbose_name='Email', unique=True
    )
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(
        max_length=20, verbose_name='Роль', choices=ROLE_CHOICES, default=USER
    )
    confirmation_code = models.CharField(
        'Код подтверждения', max_length=50, blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER
