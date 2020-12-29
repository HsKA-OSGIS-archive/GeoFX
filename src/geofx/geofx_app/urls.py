from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('api/<url_name>/polygon_create', csrf_exempt(views.PolygonCreate.as_view()), name='polygon_create'),
    path('', TemplateView.as_view(template_name="index.html")),
    path('about/', TemplateView.as_view(template_name="about.html")),
    path('map/create/', views.MapCreate.as_view()),
    path('map/<url_name>/', views.MapView.as_view()),
    path('map/<pk>/edit/', views.MapEdit.as_view()),
    path('map/<pk>/delete/', views.MapDelete.as_view()),
    path('map/<pk>/edit/polygon_create/', csrf_exempt(views.PolygonCreate.as_view()), name='polygon_create'),
    path('map_list/', views.MapList.as_view()),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('register/', views.register, name='register'),
    path('user/', views.UserOverview.as_view(), name='user_home'),
]