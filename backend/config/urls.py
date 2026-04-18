from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls_auth')),
    path('api/users/', include('apps.users.urls')),
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/deals/', include('apps.deals.urls')),
    path('api/documentos/', include('apps.documentos.urls')),
    path('api/tareas/', include('apps.tareas.urls')),
    path('api/notificaciones/', include('apps.notificaciones.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
