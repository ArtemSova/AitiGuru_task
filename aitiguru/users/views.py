from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from new_app.models import Order
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm


class LoginUser(LoginView):
    """
    Представление для входа пользователя в систему.

    Наследует стандартный LoginView Django с кастомной формой и шаблоном.

    Атрибуты:
        form_class (LoginUserForm): Кастомная форма аутентификации
        template_name (str): Путь к HTML-шаблону страницы входа
        extra_context (dict): Дополнительный контекст для шаблона
    """

    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class ProfileUser(LoginRequiredMixin, UpdateView):
    """
    Представление для просмотра и редактирования профиля пользователя.

    Требует авторизации. Пользователь может редактировать только свой профиль.

    Атрибуты:
        model: Модель пользователя
        form_class (ProfileUserForm): Форма редактирования профиля
        template_name (str): Путь к HTML-шаблону профиля
        extra_context (dict): Дополнительный контекст для шаблона

    Методы:
        get_success_url: Возвращает URL для перенаправления после успешного сохранения
        get_object: Возвращает объект текущего пользователя для редактирования
    """

    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {
        'title': "Профиль пользователя",
    }

    def get_success_url(self):
        """
        Возвращает URL для перенаправления после успешного обновления профиля.

        Returns:
            URL страницы профиля пользователя
        """

        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        """
        Возвращает объект текущего пользователя для редактирования.

        Обеспечивает, что пользователь может редактировать только свой профиль.

        Args:
            queryset: QuerySet для поиска объекта (не используется)

        Returns:
            Объект текущего аутентифицированного пользователя
        """

        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(user=self.request.user).prefetch_related('items')
        return context


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')  # Перенаправление после успешной регистрации


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
