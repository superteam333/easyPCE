from django.conf.urls import patterns, include, url
import devviews

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', pce.views.login_page),
    url(r'^(?P<dept>\w{3})/?$', devviews.dephome),
    #url(r'^(?P<dept>\w{3})/courses$', views.depcourses),
    #url(r'^(?P<dept>\w{3})/professors$', views.depprofs),
    # url(r'^myapp/', include('myapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
