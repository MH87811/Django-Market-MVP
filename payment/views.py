from django.db import transaction
from django.shortcuts import redirect, get_object_or_404

from notifications.models import Notification
from notifications.tasks import send_notification
from products.models import ProductVariant
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

class VerifyPaymentView(View):
    def get(self, request, *args, **kwargs):
        authority = request.GET.get('authority')
        if not authority:
            messages.error(request, 'payment authority is required')
            return redirect('core:home')

        payment = get_object_or_404(Payment.objects.select_related('order'), authority=authority)

        if payment.status != Payment.StatusChoices.PENDING:
            messages.error(request, 'payment has been already processed')
            return redirect('orders:detail', payment.order_id)

        # gateway.verify_payment(
        #     authority=payment.authority,
        #     amount=payment.amount,
        # )

        verification_success = True
        if not verification_success:
            payment.change_status(Payment.StatusChoices.FAILED)
            messages.error(request, 'payment failed')
            return redirect('orders:detail', payment.order_id)

        with transaction.atomic():
            payment = Payment.objects.select_for_update().select_related('order').get(pk=payment.pk)

            if payment.status != Payment.StatusChoices.PENDING:
                messages.error(request, 'payment has been already processed')
                return redirect('orders:detail', payment.order_id)

            order = Order.objects.select_for_update().get(id=payment.order_id)
            items = list(order.order_items.all())
            variant_ids = [
                item.variant_id
                for item in items
            ]

            variants = {
                variant.id: variant
                for variant in (
                    ProductVariant.objects
                    .select_for_update()
                    .select_related('product')
                    .filter(id__in=variant_ids)
                    .order_by('id')
                )
            }

            for item in items:
                variant = variants[item.variant_id]

                if not variant.product.is_available:
                    messages.error(
                        request,
                        f'{variant.product} is no longer available.'
                    )
                    return redirect(
                        'orders:detail',
                        order.id,
                    )

                if item.quantity > variant.stock:
                    messages.error(
                        request,
                        f'Not enough stock for {variant}.'
                    )
                    return redirect(
                        'orders:detail',
                        order.id,
                    )

            for item in items:
                variant = variants[item.variant_id]
                variant.stock -= item.quantity
                variant.save(update_fields=['stock'])

            payment.change_status(
                Payment.StatusChoices.SUCCESS
            )

            order.change_status(
                Order.StatusChoices.PAID
            )

            notification = Notification.objects.create(
                type=Notification.TypeChoices.PAYMENT_RECEIVED,
                title='Payment Received',
                message=f'Payment Received For Order: {order}',
                order=order,
                recipient=order.seller,
            )
            transaction.on_commit(lambda: send_notification.delay(notification.id))

        messages.success(request, 'Payment successful.')

        return redirect(
            'orders:detail',
            order.id,
        )