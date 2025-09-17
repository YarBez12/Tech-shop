from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_or_last(queryset, page_number, per_page, *, allow_empty_first_page=True, orphans=0):
    paginator = Paginator(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
    try:
        page = paginator.page(page_number or 1)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return paginator, page, page.object_list, page.has_other_pages()


def paginate_strict_for_endless(queryset, page_number, per_page):
    paginator = Paginator(queryset, per_page)
    try:
        page_num = paginator.validate_number(page_number or 1)
        page = paginator.page(page_num)
        return paginator, page, page.object_list, page.has_other_pages()
    except (PageNotAnInteger, EmptyPage):
        return paginator, None, [], False