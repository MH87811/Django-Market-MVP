from django.db.models import Count, Q
from django.views.generic import *
from orders.models import *
from products.models import *
from django.contrib.auth import get_user_model


# Create your views here.

User = get_user_model()

class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        paid_status = [
            Order.StatusChoices.PAID,
            Order.StatusChoices.SHIPPED,
            Order.StatusChoices.DELIVERED,
        ]
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'categories': Category.objects.all(),
            'new_products': Product.objects.filter(is_available=True).order_by('-created_at')[:4],
            'top_sellers': User.objects.filter(is_vendor=True).annotate(sells=Count('sell_orders', filter=Q(sell_orders__status__in=paid_status))).order_by('-sells')[:5]
        })
        return ctx