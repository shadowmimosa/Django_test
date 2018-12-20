from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('favicon.ico/',
         RedirectView.as_view(url='/static/background/images/favicon.ico')),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('image/', views.image, name='image')
]
