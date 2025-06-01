
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()


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