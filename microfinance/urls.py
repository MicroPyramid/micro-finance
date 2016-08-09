from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django_blog_it import urls as django_blog_it_urls
from front_end.views import FrontIndexView, PageView


urlpatterns = [
    url(r'^$', FrontIndexView.as_view(), name='microfinance_front_index'),
    url(r'^dashboard/', include('micro_admin.urls', namespace='micro_admin')),
    url(r'^dashboard/', include('savings.urls', namespace='savings')),
    url(r'^dashboard/', include('loans.urls', namespace='loans')),
    url(r'^finance/', include('core.urls', namespace='core')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blogs/', include(django_blog_it_urls)),

    url(r'^(?P<slug>[-\w]+)/$', PageView.as_view()),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
