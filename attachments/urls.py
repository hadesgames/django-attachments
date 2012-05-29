from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^add-for/(?P<app_label>[\w\-]+)/(?P<module_name>[\w\-]+)/(?P<pk>.*)/$', 'attachments.views.add_attachment', name="add_attachment"),
    url(r'^delete/(?P<attachment_pk>\d+)/$', 'attachments.views.delete_attachment', name="delete_attachment"),
    url(r'^get/(?P<attachment_pk>\d+)/$', 'attachments.views.retrieve_attachment', name="retrieve_attachment"),
)
