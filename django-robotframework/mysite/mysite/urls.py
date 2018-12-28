from django.conf.urls import patterns, include, url
from django.contrib import admin
from mysite.views import *
from robottest.views import *
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^index/$', index),
    url(r'^report/(\d+)/$', report),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^testrunnerselectcase/$', testrunnerselectcase),
    url(r'^testrunnerdata/$', testrunnerdata),
    url(r'^testrunnerrefresh/$', testrunnerrefresh),
    url(r'^testrunnerstart/$', testrunnerstart),
)
