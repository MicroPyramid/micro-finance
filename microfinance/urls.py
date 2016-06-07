from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
	'',
    url(r'^', include('micro_admin.urls', namespace='micro_admin')),
    url(r'^admin/', include(admin.site.urls)),
)
