from django.urls import path

from .views import ProductListView, ShowProd, CartView, AddToCartView, RemoveFromCartView, CheckoutView, UpdateQuantityView

urlpatterns = [
    # Главная страница - список всех товаров
    path("", ProductListView.as_view(), name="home"),
    path('prod/<int:prod_id>/', ShowProd.as_view(), name='produ'),
    # Страница товаров конкретной категории
    path("category/<int:cat_id>/", ProductListView.as_view(), name="category_products"),
    # Корзина пользователя
    path("cart/", CartView.as_view(), name="cart_view"),
    # Добавление товара в корзину
    path("cart/add/<int:product_id>/", AddToCartView.as_view(), name="add_to_cart"),
    # Удаление товара из корзины
    path("cart/remove/<int:item_id>/", RemoveFromCartView.as_view(), name="remove_from_cart"),
    # Обновление количества товара (увеличение/уменьшение)
    path("cart/update/<int:item_id>/<str:action>/", UpdateQuantityView.as_view(), name="update_quantity"),
    # Оформление заказа
    path("cart/checkout/", CheckoutView.as_view(), name="checkout"),
]
