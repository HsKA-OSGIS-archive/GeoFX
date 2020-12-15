from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView


from . import views


urlpatterns = [
    path('api/<url_name>/polygon_create', csrf_exempt(views.PolygonCreate.as_view()), name='polygon_create'),
    path('', TemplateView.as_view(template_name="index.html")),
    path('map/create/', views.MapCreate.as_view()),
    path('map/<url_name>/', views.MapView.as_view()),
    path('map/<pk>/edit/', views.MapEdit.as_view()),
    path('map/<pk>/edit/polygon_create/', csrf_exempt(views.PolygonCreate.as_view()), name='polygon_create'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register),
    path('user/', views.UserOverview.as_view()),
]