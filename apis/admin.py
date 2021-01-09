from django.contrib import admin

# Register your models here.
from .models import Provincia, UsuarioDomicilio,  Solicitud, \
    SolicitudMensaje, Material, SolicitudMaterial, Viaje, ViajeSolicitud


class ProvinciaAdmin(admin.ModelAdmin):
    pass


admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(UsuarioDomicilio)
admin.site.register(Solicitud)
admin.site.register(SolicitudMensaje)
admin.site.register(Material)
admin.site.register(SolicitudMaterial)
admin.site.register(Viaje)
admin.site.register(ViajeSolicitud)



