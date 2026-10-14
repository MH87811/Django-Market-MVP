from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from notifications.models import Notification
from orders.models import Order, OrderItem
from products.models import Product
from utils.vendor_view import BaseVendorView
from django.utils import timezone

# Create your views here.

class BuyerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        orders = Order.objects.filter(user=self.request.user).select_related('seller').order_by('-created_at')
        notifications = Notification.objects.filter(recipient=self.request.user)

        ctx.update({
            'orders' : orders,
            'pending_orders' : orders.filter(status=Order.StatusChoices.PENDING),
            'paid_orders' : orders.filter(status=Order.StatusChoices.PAID),
            'delivered_orders' : orders.filter(status=Order.StatusChoices.DELIVERED),
            'cancelled_orders' : orders.filter(status=Order.StatusChoices.CANCELLED),
            'notifications': notifications,
        })

        return ctx

class VendorDashboardView(BaseVendorView, TemplateView):
    template_name = 'panel/vendor-dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        orders = Order.objects.filter(seller=self.request.user).order_by('-created_at')
        notifications = Notification.objects.filter(recipient=self.request.user)
        products = Product.objects.filter(user=self.request.user)

        paid_status = [
            Order.StatusChoices.PAID,
            Order.StatusChoices.SHIPPED,
            Order.StatusChoices.DELIVERED,
        ]

        top_sale_products = OrderItem.objects.filter(
            order__seller=self.request.user,
            order__status__in=paid_status
        ).values('variant__product').annotate(
            sell_quantity=Sum('quantity')
        ).order_by('-sell_quantity')[:5]

        month_start = timezone.localtime().replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        ctx.update({
            'orders': orders,
            'recent_orders': orders[:5],
            'products': products,
            'active_products_count': products.filter(status=Product.StatusChoices.PUBLISHED).count(),
            'top_sale_products': top_sale_products,
            'low_stock_products': products.filter(stock__lt=5),
            'notifications': notifications,
            'sales_this_month': orders.filter(status=Order.StatusChoices.PAID, created_at__gt=month_start).aggregate(total=Sum('total_price'))['total'] or 0,
            # 'sales_this_week': orders.filter(status=Order.StatusChoices.PAID, created_at__gt=month_start).aggregate(total=Sum('total_price'))['total'] or 0,
        })