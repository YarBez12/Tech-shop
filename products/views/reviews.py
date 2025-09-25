from products.models import Review, ReviewImage
from django.contrib import messages
from products.forms import ReviewForm
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, UpdateView




class ReviewDelete(DeleteView):
    model = Review
    context_object_name = 'review'
    extra_context = {
        'title': 'Review delete'
    }
    
    def get_queryset(self):
        return (Review.objects
                .select_related('user','product')
                .prefetch_related('images'))
    
    def get_success_url(self):
        messages.warning(self.request, 'Review has been deleated', extra_tags='deleted')
        return self.object.get_absolute_url()
    

class ReviewEdit(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'products/review_edit.html'
    extra_context = {
        'title': 'Review update'
    }

    def get_queryset(self):
        return (Review.objects
                .select_related('user','product')
                .prefetch_related('images'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = context.get('form')
        context['existing_images'] = self.object.images.all()
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        new_images = self.request.FILES.getlist('images')
        for image in new_images:
            self.object.images.create(image=image)
        
        delete_images_ids = self.request.POST.getlist('delete_images')
        for image_id in delete_images_ids:
            image = get_object_or_404(ReviewImage, id=image_id)
            image.delete()
        messages.success(self.request, 'Review has been updated')
        
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