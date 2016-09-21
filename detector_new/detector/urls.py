from django.conf.urls import url

import views

app_name = 'detector'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^post_data/$', views.post_data, name='post_data')
]