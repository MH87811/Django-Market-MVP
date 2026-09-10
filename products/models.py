from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.

User = get_user_model()

class Category(models.Model):
    title = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='category_images')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category-detail', args=[self.slug])

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.ManyToManyField(Category, related_name='category_products')
    is_available = models.BooleanField(default=True)

    class StatusChoices(models.TextChoices):
        PUBLISHED = 'P', 'Published'
        DRAFT = 'D', 'Draft'
    status = models.CharField(max_length=1, choices=StatusChoices, default='P')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

    def get_main_image(self):
        main_image = self.images.get(is_main=True)
        if main_image:
            return main_image.image.url
        return None

    def get_all_images(self):
        return [image.image.url for image in self.images.all()]

    @property
    def total_stock(self):
        total_stock = sum(variant.stock for variant in self.variants.all())
        if total_stock > 0:
            return total_stock
        else:
            return 'unavailable'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.title)
            self.save()

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images')
    alt_text = models.CharField(max_length=64, blank=True, null=True, default=f'{product} image')
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        unique_together = ('product', 'image')

    def __str__(self):
        return f'{self.product} image'

    def save(self, *args, **kwargs):
        if self.is_main:
            self.product.images.filter(
                is_main=True
            ).exclude(
                pk=self.pk
            ).update(
                is_main=False
            )
        super().save(*args, **kwargs)

        
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=64, blank=True)
    value = models.CharField(max_length=64, blank=True)
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'name', 'value')
        ordering = ['name', 'value']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'

    def __str__(self):
        return f'{self.product} {self.name}: {self.value}'

    def get_final_price(self):
        return self.product.price + self.price_modifier

    def get_stock_display(self):
        return self.stock if self.stock > 0 else 'unavailable'