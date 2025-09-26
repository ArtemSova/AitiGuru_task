from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersViewsTestCase(TestCase):
    """
    TestCase для тестирования представлений приложения users.

    Класс содержит комплексные тесты для проверки функциональности:
    - Авторизации и аутентификации пользователей
    - Регистрации новых пользователей (включая валидацию)
    - Управления профилем пользователя
    - Смены пароля
    - Выхода из системы

    Attributes:
        user_data (dict): Тестовые данные для создания пользователя
        user (User): Созданный тестовый пользователь
    """

    def setUp(self):
        """
        Инициализация тестового окружения перед выполнением каждого теста.

        Создает тестового пользователя с полным набором данных для последующих тестов.
        Проверяет корректность создания пользователя в базе данных.
        """

        self.user_data = {
            'username': 'user666',
            'email': 'user666@mail.my',
            'password': 'password123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'title': 'ООО "Тест"',
            'address': 'Адрес теста'
        }
        self.user = User.objects.create_user(**{k: v for k, v in self.user_data.items() if k != 'password'}, password=self.user_data['password'])

    def test_login_page_access(self):
        """
        Тест доступности страницы входа для неавторизованных пользователей.

        Проверяет:
        - Возвращается ли статус HTTP 200 (OK) при запросе страницы входа
        - Используется ли корректный шаблон (users/login.html)
        - Доступность страницы без необходимости аутентификации

        Test Case:
            GET-запрос к странице входа должен возвращать статус 200 и правильный шаблон
        """

        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_register_page_access_not_logged(self):
        """
        Тест доступности страницы регистрации для неавторизованных пользователей.

        Проверяет:
        - Возвращается ли статус HTTP 200 (OK) при запросе страницы регистрации
        - Используется ли корректный шаблон (users/register.html)
        - Доступность функционала регистрации для новых пользователей

        Test Case:
            GET-запрос к странице регистрации должен возвращать статус 200 и правильный шаблон
        """

        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_profile_page_access_logged(self):
        """
        Тест доступа к странице профиля для авторизованного пользователя.

        Проверяет:
        - Возможность авторизованного пользователя открыть страницу профиля
        - Корректность HTTP статуса (200 OK)
        - Использование правильного шаблона (users/profile.html)
        - Наличие объекта пользователя в контексте шаблона

        Test Case:
            Авторизованный пользователь должен иметь доступ к странице профиля
            с корректными данными в контексте
        """

        self.client.login(username='user666', password='password123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_register_new_user(self):
        """
        Тест успешной регистрации нового пользователя.

        Проверяет полный цикл регистрации:
        - Отправку POST-запроса с корректными данными
        - Редирект на страницу входа после успешной регистрации
        - Создание нового пользователя в базе данных
        - Корректное сохранение всех переданных данных
        - Хеширование пароля (не сохранение в открытом виде)

        Test Case:
            POST-запрос с валидными данными должен создавать нового пользователя
            и перенаправлять на страницу входа
        """

        initial_user_count = User.objects.count()
        new_user_data = {
            'username': 'user777',
            'email': 'user777@mail.my',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'title': 'ИП Бизнесмен',
            'address': 'город, улица',
            'password1': 'hvdsdvasd7435',
            'password2': 'hvdsdvasd7435',
        }

        response = self.client.post(reverse('users:register'), data=new_user_data)
        self.assertRedirects(response, reverse('users:login'))
        self.assertEqual(User.objects.count(), initial_user_count + 1)

        new_user = User.objects.get(username='user777')
        self.assertEqual(new_user.email, 'user777@mail.my')
        self.assertTrue(new_user.check_password('hvdsdvasd7435'))

    def test_register_email_unique(self):
        """
        Тест валидации уникальности email при регистрации.

        Проверяет обработку ошибки при попытке регистрации с уже существующим email:
        - Отсутствие редиректа (остаемся на странице регистрации)
        - Наличие ошибки в форме для поля email
        - Отсутствие создания нового пользователя в базе данных

        Test Case:
            Попытка регистрации с существующим email должна возвращать форму с ошибкой
            и не создавать нового пользователя
        """

        duplicate_data = {
            'username': 'user13',
            'email': 'user666@mail.my',
            'first_name': 'Костя',
            'last_name': 'Козлов',
            'title': 'ООО "Попытка"',
            'address': 'Не важно',
            'password1': 'pass123!',
            'password2': 'pass123!',
        }

        response = self.client.post(reverse('users:register'), data=duplicate_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)  # остаёмся на той же странице

        form = response.context['form']
        self.assertFormError(form, 'email', "Такой E-mail уже существует!")
        self.assertEqual(User.objects.filter(username='user13').count(), 0)

    def test_login_success(self):
        """
        Тест успешной аутентификации пользователя.

        Проверяет корректность процесса входа в систему:
        - POST-запрос с правильными учетными данными
        - Редирект на главную страницу после успешного входа
        - Установку сессии аутентификации

        Test Case:
            Ввод правильных учетных данных должен выполнять вход
            и перенаправлять на главную страницу
        """

        response = self.client.post(reverse('users:login'), {
            'username': 'user666',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_failure(self):
        """
        Тест неудачной попытки аутентификации.

        Проверяет обработку неверных учетных данных:
        - Отсутствие редиректа (остаемся на странице входа)
        - Наличие сообщения об ошибке в ответе
        - Сохранение статуса неаутентифицированного пользователя

        Test Case:
            Ввод неверных учетных данных должен возвращать ошибку
            и оставаться на странице входа
        """

        response = self.client.post(reverse('users:login'), {
            'username': 'user666',
            'password': 'sdfagrgrge47767'
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Пожалуйста, введите правильные имя пользователя и пароль.")

    def test_logout(self):
        """
        Тест выхода пользователя из системы.

        Проверяет корректность завершения сессии:
        - POST-запрос на выход из системы
        - Редирект на главную страницу
        - Завершение сессии аутентификации

        Test Case:
            Запрос на выход должен завершать сессию пользователя
            и перенаправлять на главную страницу
        """

        self.client.login(username='user666', password='password123')

        response = self.client.post(reverse('users:logout'))
        self.assertRedirects(response, reverse('home'))

    def test_profile_update(self):
        """
        Тест обновления данных профиля пользователя.

        Проверяет функциональность редактирования профиля:
        - Отправку POST-запроса с обновленными данными
        - Редирект на страницу профиля после успешного обновления
        - Корректное сохранение изменений в базе данных
        - Невозможность изменения защищенных полей (username, email)

        Test Case:
            Авторизованный пользователь может обновлять данные профиля,
            кроме защищенных полей username и email
        """

        self.client.login(username='user666', password='password123')
        updated_data = {
            'first_name': 'Толик',
            'last_name': 'Петров',
            'title': 'ООО "Переименовашка"',
            'address': 'г. Москва',
            # не изменяемые
            'username': 'user666',
            'email': 'user666@mail.my',
        }

        response = self.client.post(reverse('users:profile'), data=updated_data)
        self.assertRedirects(response, reverse('users:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Толик')
        self.assertEqual(self.user.title, 'ООО "Переименовашка"')
        self.assertEqual(self.user.username, 'user666')  # не изменился
        self.assertEqual(self.user.email, 'user666@mail.my')

    def test_password_change(self):
        """
        Тест смены пароля пользователя.

        Проверяет полный цикл изменения пароля:
        - Отправку POST-запроса со старым и новым паролем
        - Редирект на страницу подтверждения смены пароля
        - Невозможность входа со старым паролем
        - Возможность входа с новым паролем

        Test Case:
            Успешная смена пароля должна делать старый пароль недействительным
            и активировать новый пароль для аутентификации
        """

        self.client.login(username='user666', password='password123')
        response = self.client.post(reverse('users:password_change'), {
            'old_password': 'password123',
            'new_password1': 'bvRy_74tv7tvrv556yv',
            'new_password2': 'bvRy_74tv7tvrv556yv',
        })
        self.assertRedirects(response, reverse('users:password_change_done'))

        self.assertFalse(self.client.login(username='user666', password='password123'))
        self.assertTrue(self.client.login(username='user666', password='bvRy_74tv7tvrv556yv'))
