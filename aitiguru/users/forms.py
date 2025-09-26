from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class LoginUserForm(AuthenticationForm):
    """
    Форма для входа пользователя в систему.

    Наследуется от стандартной AuthenticationForm Django.
    Добавляет кастомные стили и русскоязычные labels.

    Поля:
    - username: Логин пользователя
    - password: Пароль пользователя
    """

    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class ProfileUserForm(forms.ModelForm):
    """
    Форма для просмотра и редактирования профиля пользователя.

    Особенности:
    - Поля username и email недоступны для редактирования
    - Все поля имеют кастомные стили CSS
    - Русскоязычные labels для полей

    Поля:
    - username: Логин (только для чтения)
    - first_name: Имя пользователя
    - last_name: Фамилия пользователя
    - title: Наименование (Юр. лицо)
    - email: Email (только для чтения)
    - address: Адрес
    """

    username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(disabled=True, required=False, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'title', 'email', 'address']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'title': 'Наименование',
            'address': 'Адрес',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

class RegisterUserForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.

    Наследуется от стандартной UserCreationForm Django.
    Расширяет базовую форму дополнительными полями профиля пользователя.
    Включает валидацию уникальности email.

    Attributes:
        username (CharField): Логин пользователя (обязательное поле)
        password1 (CharField): Пароль пользователя (обязательное поле)
        password2 (CharField): Подтверждение пароля (обязательное поле)
        email (CharField): Email пользователя (обязательное поле)
        title (CharField): Название организации пользователя (обязательное поле)
        address (CharField): Юридический адрес пользователя (обязательное поле)
        first_name: Имя
        last_name: Фамилия

    Meta:
        model (User): Модель пользователя, связанная с формой
        fields (list): Полный список полей для регистрации
        labels (dict): Русскоязычные названия полей
        widgets (dict): Виджеты для полей с кастомными атрибутами

    Methods:
        clean_email(): Валидация уникальности email в базе данных
    """

    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    email = forms.CharField(label="E-mail", widget=forms.TextInput(attrs={'class': 'form-input'}))
    title = forms.CharField(label="Название организации", widget=forms.TextInput(attrs={'class': 'form-input'}))
    address = forms.CharField(label="Юр. адрес", widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'title', 'address', 'password1', 'password2']
        labels = {'first_name': "Имя", 'last_name': "Фамилия",}

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        """
        Валидация уникальности email адреса в базе данных.

        Проверяет, не существует ли пользователь с таким email в системе.
        Если email уже занят, вызывает ValidationError.

        Returns:
            str: Очищенное значение email, если валидация пройдена

        Raises:
            forms.ValidationError: Если email уже существует в базе данных
        """

        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email


# Класс изменения пароля
class UserPasswordChangeForm(PasswordChangeForm):
    """
    Форма для изменения пароля пользователя.

    Наследуется от стандартной PasswordChangeForm Django.
    Добавляет кастомные стили и русскоязычные labels для полей.

    Включает встроенную валидацию Django для:
    - Проверки соответствия нового пароля и его подтверждения
    - Проверки сложности пароля (минимальная длина, не только цифры и т.д.)
    - Проверки что новый пароль отличается от старого

    Attributes:
        old_password (CharField): Текущий пароль пользователя
        new_password1 (CharField): Новый пароль пользователя
        new_password2 (CharField): Подтверждение нового пароля
    """
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
