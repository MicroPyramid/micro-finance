from django import template
from micro_admin.models import *
register = template.Library()


@register.filter
def get_members_count(pk):
    group = Group.objects.get(id=pk)
    count = group.clients.all().count()
    return count
