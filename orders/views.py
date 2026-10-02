from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.generic import FormView, UpdateView
from notifications.models import Notification
from utils.tasks import send_notification
from utils.vendor_view import BaseVendorView
from .forms import *
from shopcarts.models import Cart

# Create your views here.

class CreateOrderView(LoginRequiredMixin, FormView):
    form_class = OrderCreationForm
    success_url = reverse_lazy('payment:payment')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        cart_id = self.kwargs.get('cart_id')
        cart = get_object_or_404(Cart, id=cart_id, user=self.request.user)
        kwargs['cart'] = cart
        return kwargs

    def form_valid(self, form):
        order = form.save()
        self.order_id = order.id
        messages.success(self.request, 'order created')
        return super().form_valid(form=form)

class ShipOrderView(BaseVendorView, UpdateView):
    model = Order
    form_class = ShipOrderForm

    def get_success_url(self):
        return reverse(
            'orders:seller-detail',
            kwargs={'order_id': self.object.id},
        )

    def get_object(self, queryset=None):
        return get_object_or_404(
            Order,
            id=self.kwargs.get('order_id'),
            seller=self.request.user,
            status=Order.StatusChoices.PAID
        )

    def form_valid(self, form):
        with transaction.atomic():
            self.object.tracking_code = form.cleaned_data['tracking_code']
            self.object.change_status(Order.StatusChoices.SHIPPED)

            notification = Notification.objects.create(
                type=Notification.TypeChoices.ORDER_SHIPPED,
                title='Order Shipped',
                message=f'Your order {self.object} has been shipped.',
                order=self.object,
                recipient=self.object.user,
            )

            transaction.on_commit(
                lambda: send_notification.delay(notification.id)
            )
        return redirect(self.get_success_url())