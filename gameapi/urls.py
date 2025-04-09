"""
URL configuration for gameapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from catalog.views import ProviderViewSet, GameViewSet

router = DefaultRouter()
router.register(r'providers', ProviderViewSet)
router.register(r'games', GameViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Game API",
        default_version='v1',
        description="API для управления играми и провайдерами",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Убрали явный namespace
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=1), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    path('catalog/', include('catalog.urls')),
    
]