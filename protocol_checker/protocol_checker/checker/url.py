from django.conf.urls import url

from . import views

app_name = 'checker'
urlpatterns = [
    url(r'^$', views.get_index, name='index'),

    url(r'^configs$', views.get_configs, name='config_list'),

    url(r'^config/$', views.set_config, name='config'),
    url(r'^config/(?P<config_id>[0-9]+)/$', views.set_config, name='config'),
    # url(r'^config/(?P<test_config_id>[0-9]+)/delete/$', views.delete_test_config, name='config_delete'),

    url(r'^meter/(?P<request_str>[a-z]+)/(?P<ts>[0-9]*)$', views.get_meter_request, name='meter_request'),
    url(r'^meter/(?P<request_str>[a-z]+)/$', views.get_meter_request, name='meter_request'),
]
