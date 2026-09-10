from django import forms
from .models import *


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ('name', 'value', 'price_modifier', 'stock')

ProductVariantFormset = forms.inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class ProductCreateForm(forms.ModelForm):
    main_image = forms.ImageField(required=True)
    images = MultipleImageField()
    class Meta:
        model = Product
        fields = ('title', 'description', 'price', 'category', 'is_available', 'main_image', 'images')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        product = super().save(commit=False)
        product.user = self.user
        if commit:
            product.save()
            self.save_m2m()

            main_image = self.cleaned_data.get('main_image')
            ProductImages.objects.create(product=product, image=main_image, is_main=True)

            images = self.cleaned_data.get('images') or []
            for image in images:
                ProductImages.objects.create(
                    product=product,
                    image=image
                )
        return product

class ProductImagesForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ('image', 'is_main', 'alt_text')

ProductImagesFormset = forms.inlineformset_factory(
    Product,
    ProductImages,
    form=ProductImagesForm,
    extra=3,
    can_delete=True,
)

class ProductUpdateForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Product
        fields = ('title', 'description', 'price', 'category', 'is_available')