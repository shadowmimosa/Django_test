from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favicon.ico/',
         RedirectView.as_view(url='/static/background/images/favicon.ico')),
    path('login/', views.login, name='login'),
    path('image/', views.image, name='image')
]
