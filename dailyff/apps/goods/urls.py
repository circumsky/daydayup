from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^detail/(?P<sku_id>\d+)$', views.GoodDetailView.as_view(), name='detail'),
    url(r'^list/(?P<category_id>\d+)/(?P<page>\d+)',views.ListView.as_view(),name = 'list')

]
