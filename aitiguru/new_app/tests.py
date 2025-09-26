from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from new_app.models import Product, Cart, CartItem, Order, OrderItem
from users.models import User


class GetPagesTestCase(TestCase):
    """
    TestCase для тестирования страниц веб-приложения.

    Класс содержит тесты для проверки корректности отображения
    главной страницы и работы с данными из базы данных.

    Attributes:
        fixtures (list): Список файлов с фикстурами для загрузки тестовых данных
    """

    fixtures = [
    'users.json',
    'products.json',
    'categories.json',
    'carts.json',
    'cart_items.json',
    'orders.json',
    'order_items.json',
    ]

    def setUp(self):
        """
        Инициализация перед выполнением каждого теста.
        """
        pass

    def test_mainpage(self):
        """
        Тест доступности главной страницы.

        Проверяка:
        - Возвращается ли статус HTTP 200 (OK) при запросе главной страницы
        - Корректность работы URL-роутинга для имени 'home'

        Test Case:
            GET запрос на главную страницу должен возвращать статус 200
        """

        path = reverse('home')
        response = self.client.get(path)
        self.assertTemplateUsed(response, 'new_app/products.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_data_mainpage(self):
        """
        Тест отображения данных на главной странице с пагинацией.

        Проверяет корректность отображения первых 10 товаров на главной странице.
        Использует пагинацию Django (page_obj) для сравнения с ожидаемыми данными.

        Проверка по шагам:
        1. Получаем все товары из базы с предзагрузкой категорий
        2. Выполняем запрос на главную страницу
        3. Сравниваем объекты страницы (page_obj) с первыми 10 товарами из БД

        Test Case:
            Контекст 'page_obj' должен содержать первые 10 товаров из базы данных
        """

        p = Product.objects.all().select_related('cat')
        path = reverse('home')
        response = self.client.get(path)
        self.assertQuerySetEqual(response.context['page_obj'], p[:6])

    def test_pagination(self):
        """
        Тест пагинации на конкретной странице.

        Test Case:
            Контекст 'page_obj' на странице 3 должен содержать товары [12:18]
        """

        all_products = list(Product.objects.all().select_related('cat'))
        if len(all_products) < 13:
            self.skipTest("Недостаточно товаров для проверки 3-й страницы")

        path = reverse('home')
        response = self.client.get(path, {'page': 3})
        self.assertEqual(response.status_code, HTTPStatus.OK)

        expected_page_items = all_products[12:18]  # индексы 12–17
        self.assertQuerySetEqual(response.context['page_obj'], expected_page_items)

    def test_product_detail_page(self):
        """
        Тест проверяет корректность отображения страницы товара.

        Проверка:
        - Статус код страницы - 200 OK
        - Наличие заголовка товара в HTML-ответе
        - Корректность объекта товара в контексте шаблона

        Test Case:
            При переходе на страницу товара должны отображаться корректные данные
            из модели Product.
        """

        product = Product.objects.first()
        if not product:
            self.skipTest("Нет товаров в фикстурах")

        response = self.client.get(reverse('produ', kwargs={'prod_id': product.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, product.title)
        self.assertEqual(response.context['produ'], product)

    def tearDown(self):
        """
        Завершающие действия после выполнения каждого теста.
        """
        pass


class CartAndOrderTestCase(TestCase):
    """
    TestCase для тестирования функциональности корзины и оформления заказов.

    Класс содержит комплексные тесты для проверки:
    - Добавления товаров в корзину (включая edge-cases)
    - Управления количеством товаров в корзине
    - Оформления заказов при различных сценариях
    - Взаимодействия с остатками товаров на складе

    Attributes:
        fixtures (list): Список файлов с фикстурами для загрузки тестовых данных
        user (User): Тестовый пользователь для аутентификации
        product (Product): Тестовый товар для операций с корзиной
    """

    fixtures = [
    'users.json',
    'products.json',
    'categories.json',
    'carts.json',
    'cart_items.json',
    'orders.json',
    'order_items.json',
    ]

    def setUp(self):
        """
        Инициализация тестового окружения перед выполнением каждого теста.

        Проверает:
        - Загрузку тестового пользователя из фикстур
        - Аутентификацию клиента для имитации авторизованного пользователя
        - Инициализацию тестового товара с положительным остатком
        - Проверку наличия необходимых тестовых данных

        Raises:
            AssertionError: Если в фикстурах отсутствуют товары с count > 0
        """

        self.user = User.objects.get(username="user1")
        self.client.login(username="user1", password="rfhnf666")

        self.product = Product.objects.filter(count__gt=0).first()
        assert self.product is not None, "В фикстурах должен быть хотя бы один товар с count > 0"

    def test_add_to_cart_authenticated(self):
        """
        Тест добавления товара в корзину авторизованным пользователем.

        Проверяет:
        - Успешность POST-запроса на добавление товара
        - Увеличение общего количества CartItem в системе
        - Корректное создание связи между корзиной, товаром и количеством

        Test Case:
            Авторизованный пользователь может добавить товар в корзину с указанием количества
        """

        initial_cart_items = CartItem.objects.count()
        response = self.client.post(
            reverse('add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2},
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(CartItem.objects.count(), initial_cart_items + 1)

        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_add_to_cart_not_enough_stock(self):
        """
        Тест добавления количества товара, превышающего остаток на складе.

        Проверяет механизм ограничения количества товара в корзине
        на основе доступного остатка на складе.

        Test Case:
            При попытке добавить количество больше доступного остатка,
            в корзину добавляется только доступное количество товара.
        """

        over_quantity = self.product.count + 5
        self.client.post(
            reverse('add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': over_quantity}
        )

        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, self.product.count)

    def test_add_to_cart_zero_stock(self):
        """
        Тест попытки добавления товара с нулевым остатком на складе.

        Проверяет обработку сценария, когда товар отсутствует на складе.

        Test Case:
            Товар с count=0 не должен добавляться в корзину,
            пользователь должен получить соответствующее сообщение.
        """

        self.product.count = 0
        self.product.save()

        response = self.client.post(
            reverse('add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )

        cart = Cart.objects.get(user=self.user)
        self.assertFalse(cart.items.filter(product=self.product).exists())

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("нет в наличии" in str(m) for m in messages))

    def test_remove_from_cart(self):
        """
        Тест удаления товара из корзины.

        Проверяет корректность работы механизма удаления позиций из корзины.

        Test Case:
            GET-запрос на удаление товара из корзины должен:
            - Выполнять редирект на главную страницу
            - Удалять соответствующий CartItem из базы данных
        """

        cart, _ = Cart.objects.get_or_create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        response = self.client.get(reverse('remove_from_cart', kwargs={'item_id': item.id}))
        self.assertRedirects(response, '/', fetch_redirect_response=False)

        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_update_quantity_increase(self):
        """
        Тест увеличения количества товара в корзине.

        Проверяет функциональность увеличения количества существующей позиции.

        Test Case:
            Запрос на увеличение количества должен увеличивать quantity на 1.
        """

        cart, _ = Cart.objects.get_or_create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        self.client.get(reverse('update_quantity', kwargs={'item_id': item.id, 'action': 'increase'}))

        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_update_quantity_decrease_to_zero(self):
        """
        Тест уменьшения количества товара до нуля с последующим удалением.

        Проверяет edge-case: когда количество уменьшается до 0,
        позиция должна автоматически удаляться из корзины.

        Test Case:
            Уменьшение quantity с 1 до 0 должно приводить к удалению CartItem.
        """

        cart, _ = Cart.objects.get_or_create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        self.client.get(reverse('update_quantity', kwargs={'item_id': item.id, 'action': 'decrease'}))

        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

    def test_checkout_creates_order(self):
        """
        Тест успешного оформления заказа.

        Проверяет полный цикл оформления заказа:
        - Создание Order и OrderItem на основе корзины
        - Уменьшение остатков товаров на складе
        - Очистку корзины после успешного оформления

        Test Case:
            Корректное оформление заказа должно создавать новые сущности
            Order и OrderItem, уменьшать остатки товаров и очищать корзину.
        """

        Order.objects.filter(user=self.user).delete()
        CartItem.objects.filter(cart__user=self.user).delete()

        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        initial_order_count = Order.objects.count()
        initial_order_item_count = OrderItem.objects.count()
        initial_product_count = self.product.count

        response = self.client.post(reverse('checkout'))
        self.assertRedirects(response, reverse('cart_view'))

        self.assertEqual(Order.objects.count(), initial_order_count + 1)
        self.assertEqual(OrderItem.objects.count(), initial_order_item_count + 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.count, initial_product_count - 1)

        self.assertFalse(cart.items.exists())

    def test_checkout_empty_cart(self):
        """
        Тест попытки оформления заказа с пустой корзиной.

        Проверяет обработку некорректного сценария использования.

        Test Case:
            При попытке оформления пустой корзины:
            - Не должен создаваться новый заказ
            - Пользователь должен получить сообщение об ошибке
            - Должен происходить редирект на страницу корзины
        """

        initial_order_count = Order.objects.filter(user=self.user).count()

        cart = Cart.objects.filter(user=self.user).first()
        if cart:
            cart.items.all().delete()

        response = self.client.post(reverse('checkout'), follow=True)

        messages = list(response.context['messages'])
        self.assertTrue(any("Ваша корзина пуста" in str(m) for m in messages))

        self.assertEqual(Order.objects.filter(user=self.user).count(), initial_order_count)

    def test_checkout_low_stock(self):
        """
        Тест оформления заказа при недостаточном количестве товара на складе.

        Проверяет валидацию доступности товара перед созданием заказа.

        Test Case:
            При недостатке товара на складе:
            - Заказ не должен создаваться
            - Пользователь должен получить сообщение об ошибке
            - Остатки товара не должны изменяться
        """

        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=self.product.count + 1)

        initial_order_count = Order.objects.filter(user=self.user).count()

        response = self.client.post(reverse('checkout'), follow=True)

        self.assertEqual(Order.objects.filter(user=self.user).count(), initial_order_count)

        messages = list(response.context['messages'])
        self.assertTrue(any("Недостаточно товара" in str(m) for m in messages))

    def tearDown(self):
        """
        Завершающие действия после выполнения каждого теста.
        """
        pass
