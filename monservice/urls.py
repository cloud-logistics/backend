from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from monservice import views

urlpatterns = [
    url(r'^auth$', obtain_jwt_token),
    url(r'^containers$', views.containers_overview),
    url(r'^satellites$', views.satellites_overview),
]