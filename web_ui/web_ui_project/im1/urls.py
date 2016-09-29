from django.conf.urls import url

from . import views

app_name = 'im1'
urlpatterns = [
    # ex: /im1/
    url(r'^$', views.index, name='index'),
    url(r'^json/$', views.json_response, name='json'),
    # url(r'^observed/$', views.observed, name='observed'),
    url(r'^post_data/$', views.post_data, name='post_data'),
]

