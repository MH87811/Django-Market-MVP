from django.shortcuts import redirect, get_object_or_404
from .models import *
from orders.models import *
from django.views import View
from django.contrib import messages
from .gateway import PaymentGateway

# Create your views here.

class PaymentView(View):
    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        if order.status != order.StatusChoices.PENDING:
            messages.error(request, 'Order is not payable.')
            return redirect('orders:detail', order_id)

        amount = order.total_price
        payment, _ = Payment.objects.get_or_create(
            order=order,
            status=Payment.StatusChoices.PENDING,
            defaults={
                'amount': amount
            }
        )
        gateway = PaymentGateway()

        if payment.authority:
            return redirect(gateway.get_payment_url(payment.authority))

        gateway_response = gateway.request_payment(
            amount=payment.amount,
            callback_url='application'
        )

        payment.authority = gateway_response.authority
        payment.save(update_fields=['authority', 'updated_at'])

        return redirect(gateway.get_payment_url(payment.authority))
