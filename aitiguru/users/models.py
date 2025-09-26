from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Наследуется от AbstractUser Django и добавляет дополнительные поля
    для хранения информации о пользователе.

    Стандартные поля (от AbstractUser):
    - username, email, first_name, last_name
    - password, groups, user_permissions
    - is_staff, is_active, is_superuser
    - last_login, date_joined

    Дополнительные поля:
    - title: Должность или наименование организации
    - address: Физический адрес пользователя
    """

    title = models.CharField(max_length=200, blank=True, null=True, verbose_name = 'Наименование')
    address = models.CharField(max_length=200, verbose_name = 'Адрес')
