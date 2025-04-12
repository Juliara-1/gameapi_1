from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views import ProviderViewSet, GameViewSet, SearchQueryView
from .views import test_cache
from . import views

app_name = 'catalog' 

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'games', GameViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((router.urls, 'api'), namespace='api')),
    path('test-cache/', views.test_cache_view, name='test-cache'),
    path('api/search/', SearchQueryView.as_view(), name='search'),
]
