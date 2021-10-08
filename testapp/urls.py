from django.contrib import admin
from django.urls import path, include
from testapp import views


urlpatterns = [
    
    path('', views.home, name ="homepage"),
    path('login', views.login_request, name ="login"),
    path('listing', views.listing, name ="listing"),
    path('logout', views.logout_view, name ="logout"),
]


