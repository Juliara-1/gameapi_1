from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views import  SearchQueryView
from . import views

app_name = 'catalog' 

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((router.urls, 'api'), namespace='api')),
    path('api/search/', SearchQueryView.as_view(), name='search'),
]