from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users.

    Настройки:
    - default_auto_field: тип автоматического поля для первичных ключей моделей
    - name: имя приложения (должно совпадать с именем директории)
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
