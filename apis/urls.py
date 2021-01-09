from django.urls import path
from .views import ProvinciaList, UsuarioDomicilioList, SolicitudMensajeList, \
    SolicitudList, SolicitudMaterialList, ViajeSolicitudList, MaterialList, ViajeList, ApiUsuario, registrar_usuario, \
    crear_solicitud, solicitudes_pendientes
from rest_framework.authtoken import views

urlpatterns = [
    # Register / Login / Users
    path('registrar_usuario/', registrar_usuario, name='alta usuario'),
    path('login/', views.obtain_auth_token, name='login'),
    path('usuarios/<int:pk>', ApiUsuario.as_view()),

    # Admin Lists
    path('provincias', ProvinciaList.as_view()),
    path('materiales', MaterialList.as_view()),


    # Gestión de solicitudes
    path('crear_solicitud', crear_solicitud),
    path('solicitudes_pendientes', solicitudes_pendientes),
    path('solicitudes', SolicitudList.as_view()),
    path('solicitud_materiales', SolicitudMaterialList.as_view()),
    path('solicitudes_mensajes', SolicitudMensajeList.as_view()),
    path('viajes', ViajeList.as_view()),
    path('viajes_solicitudes', ViajeSolicitudList.as_view()),




]

