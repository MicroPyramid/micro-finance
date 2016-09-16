from django import template
from django.db.models import Prefetch


register = template.Library()


@register.filter
def get_range(value):
    return range(value)