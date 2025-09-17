# utils/mixins.py
from django.http import HttpResponse
from .pagination import paginate_strict_for_endless, paginate_or_last

class EndlessPaginationMixin:
    endless_param = 'products_only'  

    def is_endless(self):
        return self.request.GET.get(self.endless_param)

    def paginate_queryset(self, queryset, page_size):
        page = self.request.GET.get(self.page_kwarg)
        if self.is_endless():
            return paginate_strict_for_endless(queryset, page, page_size)
        return paginate_or_last(queryset, page, page_size)

    def render_to_response(self, context, **response_kwargs):
        if self.is_endless():
            page = context.get('page_obj')
            if not page or not page.object_list:
                return HttpResponse('')
        return super().render_to_response(context, **response_kwargs)