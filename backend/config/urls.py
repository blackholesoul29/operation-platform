from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clientes/',     include('apps.clientes.urls')),
    path('api/proyectos/',    include('apps.proyectos.urls')),
    path('api/contratos/',    include('apps.contratos.urls')),
    path('api/liquidaciones/',include('apps.liquidaciones.urls')),
    path('api/cgm/',          include('apps.cgm.urls')),
    path('api/monitoreo/',    include('apps.monitoreo.urls')),
    path('api/documentos/',   include('apps.documentos.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
