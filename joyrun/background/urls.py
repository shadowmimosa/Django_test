from django.urls import path
from django.views.generic import RedirectView

from .activator import process

app_name = 'background'

urlpatterns = [
    path('', RedirectView.as_view(url='/index/')),
    path('favicon.ico',
         RedirectView.as_view(url='/static/background/images/favicon.ico')),
    path('<str:function>/', process, name='function'),
    path('<str:function>/<int:index>/', process, name='list'),

    # path('', views.index, name='index'),
    # path('index/', views.index, name='index'),
    # path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
    # path('image/', views.image, name='image')
]
