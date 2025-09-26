from django.shortcuts import render, redirect
from products.models import Product, ReviewImage, ProductImage, ProductActivationRequest, ProductCharacteristic
from products.forms import ReviewForm, ProductForm
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, BooleanField, Q, Count, Prefetch
from itertools import chain
from products.recommender import Recommender
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from products.utils.redis_utils import zincrby_product_view, zincrby_category_view, get_product_views
from products.utils.filters import get_prefetched_characteristics_query
from products.utils.filters import get_prefetched_images_query


class ProductDetailView(DetailView, FormMixin):
    model = Product
    template_name = 'products/product.html'
    context_object_name = 'product'
    form_class = ReviewForm

    def get_success_url(self):
        return self.request.path_info

    def get_object(self, queryset = ...):
        self._obj = (Product.objects
                    .select_related('brand','category','category__parent','user')
                    .prefetch_related('images','tags', get_prefetched_characteristics_query())
                    .get(slug=self.kwargs['product_slug']))
        return self._obj
    
    def get_context_data(self, **kwargs):
        product = self.get_object()
        if not self.request.GET:
            zincrby_product_view(product.id)
            zincrby_category_view(product.category.id)
        context = super().get_context_data(**kwargs)
        r = Recommender()
        recommended_bought_products = r.suggest_products_for([product], 8)
        recommended_tag_related_products = Product.objects.exclude(pk=product.pk)\
            .prefetch_related(get_prefetched_images_query())\
            .filter(tags__in=product.tags.all(), is_active=True)\
            .annotate(same_tags=Count('tags', filter=Q(tags__in=product.tags.all())))\
            .order_by('-same_tags')\
            .distinct()
        recommended_category_related_products = Product.objects.prefetch_related(get_prefetched_images_query()).filter(category=product.category, is_active=True)\
            .exclude(pk=product.pk)\
            .exclude(id__in=recommended_tag_related_products.values_list('id', flat=True))
        recommended_products = list(chain(recommended_bought_products, recommended_tag_related_products, recommended_category_related_products))[:8]
        product = self.get_object()
        session_key = f"ui_state:product:{product.slug}"
        ui_state = self.request.session.get(session_key, {})
        rating = ui_state.get('rating')
        reviews = (product.reviews
                .select_related('user')
                .prefetch_related('images')
                .annotate(
                    is_current_user=Case(
                        When(user=self.request.user, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    ))
                .order_by('-is_current_user', '-created_at'))
        if rating:
            reviews = reviews.filter(grade=rating)
        context['reviews'] = reviews
        context['title'] = product.title
        context['review_form'] = self.get_form()
        context['recommended_products'] = recommended_products
        context['small_images'] = product.images.all()[1:4]
        context['product_views'] = get_product_views(product.id)
        context['ui_state'] = ui_state
        return context
    
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            images = request.FILES.getlist('images')
            for image in images:
                ReviewImage.objects.create(review=review, image=image)
            messages.success(self.request, 'Your review has succesfully added')
            return self.form_valid(form)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                field_label = field if field != '__all__' else 'General'
                error_messages.append(f"{field_label}: {', '.join(errors)}")
            full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
            messages.error(self.request, full_error_message)
            return self.form_invalid(form)
        

class ProductDeactivate(LoginRequiredMixin, View):

    template_name = "products/product_deactivate_confirm.html"

    def get(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, user=request.user)
        context = {
            "product": product,
            "title": "Deactivate product",
        }
        return render(request, self.template_name, context)

    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, user=request.user)
        product.is_active = False
        product.quantity = 0
        product.save(update_fields=["is_active", "quantity"])

        messages.warning(request, "Product has been deactivated (hidden from catalog).", extra_tags="deleted",)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("users:profile")
    


class RequestActivationView(LoginRequiredMixin, View):
    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)

        if product.is_active:
            messages.info(request, "The product is already active.")
            return redirect(product.get_absolute_url())
        exists = ProductActivationRequest.objects.filter(
            product=product, user=request.user, status='pending'
        ).exists()
        if exists:
            messages.info(request, "You already have a pending activation request for this product.")
            return redirect(product.get_absolute_url())

        req = ProductActivationRequest.objects.create(
            product=product, user=request.user, status='pending'
        )

        messages.success(request, "Activation request has been sent. We'll review it soon.")
        return redirect(product.get_absolute_url())
class ProductEdit(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_edit.html'
    extra_context = {
        'title': 'Update review'
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_form'] = context.get('form')
        context['existing_images'] = self.object.images.all()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        new_images = self.request.FILES.getlist('images')
        for image in new_images:
            self.object.images.create(image=image)
        
        delete_images_ids = self.request.POST.getlist('delete_images')
        for image_id in delete_images_ids:
            image = get_object_or_404(ProductImage, id=image_id)
            image.delete()
        messages.success(self.request, 'Product has been updated')
        
        return response
    def form_invalid(self, form):
        response = super().form_invalid(form)
        error_messages = []
        for field, errors in form.errors.items():
            field_label = field if field != '__all__' else 'General'
            error_messages.append(f"{field_label}: {', '.join(errors)}")
        full_error_message = "Please correct the following errors: " + "; ".join(error_messages)
        messages.error(self.request, full_error_message)

        return response