from django import template
from micro_admin.models import Menu
from django.db.models import Prefetch


register = template.Library()


@register.filter
def get_range(value):
    return range(value)


@register.assignment_tag()
def get_menus():
    menu_list = Menu.objects.filter(status="on").prefetch_related(
        Prefetch("menu_set", queryset=Menu.objects.filter(
            status="on").order_by('lvl'), to_attr="active_children"
        )
    )
    return menu_list.filter(parent=None, status="on").order_by('lvl')
