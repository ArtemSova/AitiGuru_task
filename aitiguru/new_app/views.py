from django.contrib import messages
from django.views.generic import ListView, RedirectView, View, DetailView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Product, Category, Cart, CartItem, Order, OrderItem


class ProductListView(ListView):
    """
    Отображение списка товаров.
    Показывает все товары или товары определенной категории с учетом иерархии.
    """

    model = Product
    template_name = "new_app/products.html"
    title_page = 'Главная страница'
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        """Возвращает товары с фильтрацией по категории."""
        cat_id = self.kwargs.get("cat_id")
        if cat_id:
            category = get_object_or_404(Category, id=cat_id)
            categories = category.get_descendants(include_self=True)
            return Product.objects.filter(cat__in=categories).select_related("cat")
        return Product.objects.select_related("cat").all()

    def get_context_data(self, **kwargs):
        """Добавляет в контекст данные о категориях для навигации."""
        context = super().get_context_data(**kwargs)
        cat_id = self.kwargs.get("cat_id")
        if cat_id:
            current_category = get_object_or_404(Category, id=cat_id)
            context["current_category"] = current_category
            context["ancestors"] = current_category.get_ancestors(include_self=True)
        else:
            context["current_category"] = None
            context["ancestors"] = []
        context["root_categories"] = Category.objects.root_nodes()
        return context

class ShowProd(DetailView):
    template_name = 'new_app/prod.html'
    pk_url_kwarg = 'prod_id'
    context_object_name = 'produ'

    def get_object(self, queryset=None):     # запрет показа неопубликованных статей
        return get_object_or_404(Product.objects, pk=self.kwargs[self.pk_url_kwarg])

class CartView(LoginRequiredMixin, ListView):
    """
    Отображение корзины пользователя.
    Требует авторизации. Показывает все товары в корзине текущего пользователя.
    """

    model = CartItem
    template_name = "new_app/cart.html"
    context_object_name = "items"

    def get_queryset(self):
        """Возвращает товары из корзины текущего пользователя."""
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def get_context_data(self, **kwargs):
        """Добавляет объект корзины в контекст."""
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        context["cart"] = cart
        return context


class AddToCartView(LoginRequiredMixin, RedirectView):
    """
    Добавление товара в корзину.
    Требует авторизации. Обрабатывает POST-запросы для добавления товара.
    Проверяет доступное количество товара.
    """

    pattern_name = "cart_view"

    def post(self, request, *args, **kwargs):
        """Обрабатывает добавление товара в корзину."""
        product = get_object_or_404(Product, id=kwargs["product_id"])
        cart, _ = Cart.objects.get_or_create(user=request.user)

        if product.count <= 0:
            messages.error(request,f"Товара «{product.title}» нет в наличии.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1

        if quantity > product.count:
            messages.error(request, f"В наличии только {product.count} шт.")
            quantity = product.count

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            item.quantity = quantity
        else:
            new_quantity = item.quantity + quantity
            if new_quantity > product.count:
                messages.error(request, f"Максимум доступно {product.count} шт.")
                item.quantity = product.count
            else:
                item.quantity = new_quantity
        item.save()

        return redirect(request.META.get("HTTP_REFERER", "/"))


class RemoveFromCartView(LoginRequiredMixin, RedirectView):
    """
    Удаление товара из корзины.
    Требует авторизации. Удаляет указанный товар из корзины пользователя.
    """

    def get_redirect_url(self, *args, **kwargs):
        """Удаляет товар из корзины."""
        item = get_object_or_404(CartItem, id=kwargs["item_id"], cart__user=self.request.user)
        item.delete()

        return self.request.META.get("HTTP_REFERER", "/")


class UpdateQuantityView(LoginRequiredMixin, View):
    """
    Изменение количества товара в корзине.
    Требует авторизации. Увеличивает или уменьшает количество товара.
    При уменьшении до 0 удаляет товар из корзины.
    """

    def get(self, request, *args, **kwargs):
        """Обрабатывает изменение количества товара."""
        item = get_object_or_404(CartItem, id=kwargs["item_id"], cart__user=request.user)
        action = kwargs["action"]

        if action == "increase":
            item.quantity += 1
            item.save()
        elif action == "decrease":
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()

        return redirect("cart_view")


class CheckoutView(LoginRequiredMixin, View):
    """
    Оформление заказа.
    Требует авторизации. Создает заказ на основе товаров в корзине,
    уменьшает остатки товаров и очищает корзину.
    """

    def post(self, request, *args, **kwargs):
        """Обрабатывает оформление заказа."""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            messages.error(request, "Ваша корзина пуста")
            return redirect("cart_view")

        insufficient_items = []
        for item in cart.items.all():
            if item.quantity > item.product.count:
                insufficient_items.append(f"{item.product.title} (доступно: {item.product.count})")

        if insufficient_items:
            messages.error(request, f"Недостаточно товара: {', '.join(insufficient_items)}")
            return redirect("cart_view")

        order = Order.objects.create(user=request.user)

        try:
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    cat=item.product.cat,
                    quantity=item.quantity,
                    price=item.product.price
                )

                item.product.count -= item.quantity
                item.product.save()

            cart.items.all().delete()

            messages.success(request, f"Заказ {order.order_number} успешно оформлен!")
            return redirect("cart_view")

        except Exception as e:
            order.delete()
            messages.error(request, f"Произошла ошибка при оформлении заказа: {str(e)}")
            return redirect("cart_view")
