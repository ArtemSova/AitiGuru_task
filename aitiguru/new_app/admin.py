from django.contrib import admin

from .models import Product, Category, Cart, CartItem, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления товарами (Product).

    Настройки:
    - Отображаемые поля: ID, название, цена, количество, категория
    - Ссылки для редактирования: ID и название
    - Сортировка по названию
    - Пагинация: 10 записей на страницу
    """

    list_display = ('id', 'title', 'price', 'count', 'cat')
    list_display_links = ('id', 'title')
    ordering = ['title']
    list_per_page = 10

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления категориями (Category).

    Настройки:
    - Отображаемые поля: ID, название, родительская категория
    - Ссылки для редактирования: ID и название
    """

    list_display = ('id', 'title', 'parent')
    list_display_links = ('id', 'title')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления корзинами (Cart).

    Настройки:
    - Отображаемые поля: ID, пользователь, дата создания
    - Ссылки для редактирования: ID и пользователь
    """

    list_display = ('id', 'user', 'created_at')
    list_display_links = ('id', 'user')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления элементами корзины (CartItem).

    Настройки:
    - Отображаемые поля: ID, корзина, товар, количество
    - Ссылки для редактирования: ID
    """

    list_display = ('id', 'cart', 'product', 'quantity')
    list_display_links = ('id', )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления заказами (Order).

    Настройки:
    - Отображаемые поля: ID, номер заказа, пользователь, дата создания
    - Ссылки для редактирования: ID и номер заказа
    """

    list_display = ('id', 'order_number', 'user', 'created_at')
    list_display_links = ('id', 'order_number',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления элементами заказа (OrderItem).

    Настройки:
    - Отображаемые поля: ID, заказ, товар, количество, цена
    - Ссылки для редактирования: ID и заказ
    """

    list_display = ('id', 'order', 'product', 'quantity', 'price')
    list_display_links = ('id', 'order')
