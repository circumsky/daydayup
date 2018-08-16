from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^register$', views.RegisterUser.as_view(), name='register'),
    url(r'^active/(?P<active_token>.+)$', views.ActiveUser.as_view(), name='active')
]
