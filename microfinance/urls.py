from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^', include('micro_admin.urls', namespace='micro_admin')),
    url(r'^', include('savings.urls', namespace='savings')),
    url(r'^', include('loans.urls', namespace='loans')),
    url(r'^finance/', include('core.urls', namespace='core')),
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
