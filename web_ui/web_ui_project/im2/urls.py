from django.conf.urls import url

from . import views

app_name = 'im2'
urlpatterns = [
    # ex: /im1/
    url(r'^$', views.index, name='index'),
    url(r'^post_data/$', views.post_data, name='post_data'),
]

