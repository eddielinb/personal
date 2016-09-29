from django.conf.urls import url

from . import views

app_name = 'gdrive1'
urlpatterns = [
    # ex: /gdrive1/
    url(r'^$', views.index, name='index'),
    url(r'^json/$', views.json_response, name='json'),
    url(r'^post_data/$', views.post_data, name='post_data'),
]
