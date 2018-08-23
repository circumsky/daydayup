from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^register$', views.RegisterUser.as_view(), name='register'),
    url(r'^active/(?P<active_token>.+)$', views.ActiveUser.as_view(), name='active'),
    url(r'^login$', views.LoginView.as_view(),name='login'),
    url(r'^logout$', views.LogoutView.as_view(),name='logout'),
    url(r'^address', views.AddressView.as_view(),name='address'),
    url(r'^info', views.InfoView.as_view(),name='info'),
]
