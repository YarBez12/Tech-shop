import math
import re
from django import template
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from datetime import date
from datetime import datetime
from django.utils import timezone


register = template.Library()


@register.filter()
def get_item(queryset, index):
    return queryset[int(index)]


@register.filter
def floor_int(value):
    try:
        return math.floor(float(value))
    except (ValueError, TypeError):
        return value
    
@register.filter
def ceil_int(value):
    try:
        return math.ceil(float(value))
    except (ValueError, TypeError):
        return value
    
@register.filter
def get_item_from_dict(dictionary, key):
    return dictionary.get(key, [])



@register.simple_tag(takes_context=True)
def change_params(context, **kwargs):
    query = context['request'].GET.copy()  
    for key, value in kwargs.items():
        query.setlist(key, value if isinstance(value, list) else [value]) 
    return urlencode(query, doseq=True) 


@register.filter()
def highlight(text, query):
    if not text:
        return ""
    if not query:
        return text
    terms = [re.escape(t) for t in str(query).split() if t.strip()]
    if not terms:
        return text
    pattern = re.compile(r'(' + '|'.join(terms) + r')', re.IGNORECASE)

    def repl(m):
        return f'<mark class="hl">{m.group(0)}</mark>'

    return mark_safe(pattern.sub(repl, str(text)))

@register.filter
def days_since(value):
    if not value:
        return ""
    if isinstance(value, datetime):
        val_date = timezone.localtime(value).date()
    else:
        val_date = value
    today = timezone.localdate()
    diff = (today - val_date).days
    if diff <= 0:
        return "less than a day"
    return f"{diff} day{'s' if diff > 1 else ''}"