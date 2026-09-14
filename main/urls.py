from django.urls import path
from main import views

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots'),
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('policies/', views.policy_menu, name='policy_menu'),
    path('policies/<str:policy_slug>/', views.get_policy, name='get_policy'),
]
