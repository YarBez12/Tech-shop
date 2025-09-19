from django import template
import os
from django import template


register = template.Library()
@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None

@register.filter
def basename(value: str) -> str:
    return os.path.basename(value or "")