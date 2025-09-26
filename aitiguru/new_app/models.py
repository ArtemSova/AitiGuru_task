import uuid

from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey


class Product(models.Model):
    """
    Модель товара.

    Атрибуты:
    - title: Наименование товара (уникальное)
    - cat: Категория товара
    - count: Количество на складе
    - price: Цена товара
    """

    title = models.CharField(max_length=255, unique=True, blank=False, verbose_name = 'Наименование')
    cat = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name = 'Категория')
    count = models.IntegerField(verbose_name = 'Количество')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name = 'Цена')

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Category(MPTTModel):
    """
    Модель категории товаров с поддержкой иерархии (MPTT) для ссылок на другую категорию.

    Атрибуты:
    - title: Название категории
    - parent: Родительская категория (для создания дерева категорий)

    Свойства:
    - children_count: Количество дочерних категорий
    """

    title = models.CharField(max_length=100, unique=False, verbose_name = 'Название')   # Некот подкатегории могут совпадать(диагон разн ноутбуков)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
                            blank=True, related_name='children', verbose_name = 'Родитель',)

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title

    @property
    def children_count(self):
        """Количество прямых дочерних категорий."""
        return self.get_children().count()


class Cart(models.Model):
    """
    Модель корзины покупок клиента.

    Атрибуты:
    - user: Владелец корзины
    - created_at: Дата создания корзины

    Свойства:
    - total_price: Общая стоимость всех товаров в корзине
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                blank=False, related_name="cart", verbose_name="Покупатель")

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        """Общая сумма корзины"""
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Корзина {self.user.username}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    """
    Модель элемента корзины (отдельный товар в корзине).

    Атрибуты:
    - cart: Корзина, к которой принадлежит элемент
    - product: Товар
    - quantity: Количество товара

    Свойства:
    - price: Цена за единицу товара
    - total_price: Общая стоимость позиции (цена × количество)
    """

    cart = models.ForeignKey( Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    @property
    def price(self):
        """Цена одного товара"""
        return self.product.price

    @property
    def total_price(self):
        """Цена с учетом количества"""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} ({self.quantity} шт.)"

    class Meta:
        verbose_name = "Товар корзины"
        verbose_name_plural = "Товары корзины"



class Order(models.Model):
    """
    Модель заказа пользователя.

    Атрибуты:
    - order_number: Уникальный номер заказа (генерируется автоматически)
    - user: Заказчик
    - created_at: Дата создания заказа

    Свойства:
    - total_sum: Общая сумма заказа
    """

    order_number = models.CharField(max_length=36, default=uuid.uuid4, unique=True, verbose_name="Номер заказа")
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Заказчик")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_sum(self):
        """Общая сумма заказа"""
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Заказ {self.order_number} ({self.user.username})"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    """
    Модель элемента заказа (отдельный товар в заказе).

    Атрибуты:
    - order: Заказ, к которому принадлежит элемент
    - product: Товар
    - cat: Категория товара (дублируется для истории)
    - quantity: Количество товара
    - price: Цена на момент заказа (фиксируется)

    Свойства:
    - total_price: Общая стоимость позиции в заказе
    """

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    quantity = models.PositiveIntegerField(verbose_name="Количество товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    @property
    def total_price(self):
        """ Общая стоимость заказа """
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

    class Meta:
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"


