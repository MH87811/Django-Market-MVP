from products.models import Category

def global_category(request):
    return {
        'categories': Category.objects.all()
    }