from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('fleet.urls')),
    path('api/', include('telemetry.urls')),
    path('api/', include('predictions.urls')),
    path('api/', include('reports.urls')),
    path('api/legacy/', include('api.urls')), # preserve existing api logic temporarily
]
