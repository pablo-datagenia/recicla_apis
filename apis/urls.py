from django.urls import path
from .views import ProvinciaList, UsuarioList, UsuarioDomicilioList, UsuarioRolList, SolicitudMensajeList, \
    SolicitudList, SolicitudMaterialList, ViajeSolicitudList, MaterialList, ViajeList, ApiUsuario, registrar_usuario
from rest_framework.authtoken import views

urlpatterns = [
    # Register / Login / Users
    path('registrar_usuario/', registrar_usuario, name='alta usuario'),
    path('login/', views.obtain_auth_token, name='login'),
    path('usuarios', UsuarioList.as_view()),
    path('usuarios/<int:pk>', ApiUsuario.as_view()),

    # Admin Lists
    path('provincias', ProvinciaList.as_view()),
    path('roles', UsuarioRolList.as_view()),

    path('usuarios_domicilios', UsuarioDomicilioList.as_view()),
    path('solicitudes', SolicitudList.as_view()),
    path('solicitud_materiales', SolicitudMaterialList.as_view()),
    path('solicitudes_mensajes', SolicitudMensajeList.as_view()),
    path('viajes', ViajeList.as_view()),
    path('viajes_solicitudes', ViajeSolicitudList.as_view()),

    path('materiales', MaterialList.as_view()),



]

