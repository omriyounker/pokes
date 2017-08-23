from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'register', views.register),
    url(r'login', views.login),
    url(r'logout', views.logout),
    url(r'pokeuser$', views.pokeotheruser),
    url(r'pokes', views.displaypokes)
    ]
