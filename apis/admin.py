from django.contrib import admin

# Register your models here.
from .models import Provincia, UsuarioPunto,  Solicitud, \
    SolicitudMensaje, Material, Viaje, ViajeSolicitud, PuntoRecoleccion


class ProvinciaAdmin(admin.ModelAdmin):
    pass


admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(UsuarioPunto)
admin.site.register(PuntoRecoleccion)
admin.site.register(Solicitud)
admin.site.register(SolicitudMensaje)
admin.site.register(Material)
admin.site.register(Viaje)
admin.site.register(ViajeSolicitud)



