from django.shortcuts import  get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import *
from django.urls import reverse_lazy
from .forms import *

# Create your views here.

class BaseVendorView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_vendor

class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'

    def get_queryset(self):
        return Product.objects.filter(status=Product.StatusChoices.PUBLISHED)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_owner'] = self.object.user == self.request.user
        return ctx


class AddProductView(BaseVendorView, FormView):
    template_name = 'vendors/products/add.html'
    form_class = ProductCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if not 'formset' in ctx:
            ctx['formset'] = ProductVariantFormset(prefix='variant')
        return ctx

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        formset = ProductVariantFormset(request.POST, request.FILES, prefix='variant')

        is_form_valid = form.is_valid()
        is_formset_valid = formset.is_valid()
        if is_form_valid and is_formset_valid:
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        with transaction.atomic():
            product = form.save()
            formset.instance = product
            formset.save()
        messages.success(self.request, 'product created')
        return redirect('products:detail', slug=product.slug)

    def form_invalid(self, form, formset):
        ctx = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(ctx)

class ProductUpdateView(BaseVendorView, UpdateView):
    model = Product
    template_name = 'vendors/products/update.html'
    form_class = ProductUpdateForm

    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs.get('slug'), user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if 'images_formset' not in ctx:
            ctx['images_formset'] = ProductImagesFormset(prefix='images', instance=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ProductImagesFormset(request.POST, request.FILES, prefix='images', instance=self.object)

        is_form_valid = form.is_valid()
        is_formset_valid = formset.is_valid()
        if is_form_valid and is_formset_valid:
            return self.form_valid(form, formset)
        return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        with transaction.atomic():
            form.save()
            formset.save()
        return redirect('products:detail', slug=self.object.slug)

    def form_invalid(self, form, formset):
        ctx = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(ctx)

class ProductDeleteView(BaseVendorView, DeleteView):
    model = Product
    success_url = reverse_lazy('products:list')

    def get_object(self, queryset=None):
        return get_object_or_404(Product, slug=self.kwargs.get('slug'), user=self.request.user)

class AddVariantView(BaseVendorView, FormView):
    template_name = 'vendors/products/variant/add.html'
    form_class = ProductVariantForm

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.product.slug})

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, user=request.user, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.product = self.product
        form.save()
        messages.success(self.request, 'variant added')
        return super().form_valid(form)

class VariantUpdateView(BaseVendorView, UpdateView):
    model = ProductVariant
    template_name = 'vendors/products/variant/update.html'
    form_class = ProductVariantForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=self.kwargs.get('slug'), user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.kwargs.get('slug')})

    def get_object(self, queryset=None):
        return get_object_or_404(ProductVariant, product=self.product, pk=self.kwargs.get('id'))

class VariantDeleteView(BaseVendorView, DeleteView):
    model = ProductVariant

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.product.slug})

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, slug=self.kwargs.get('slug'), user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            ProductVariant,
            product=self.product,
            pk=self.kwargs.get('id'),
        )