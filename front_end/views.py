from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from micro_admin.models import Page


class FrontIndexView(TemplateView):
    template_name = 'frontend/index.html'


class PageView(DetailView):
    model = Page
    slug = 'slug'
    template_name = "frontend/page.html"
    context_object_name = 'page'
