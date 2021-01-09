from django.urls import path
from .views import ProvinciaList, SolicitudMensajeList, \
    SolicitudList, ViajeSolicitudList, MaterialList, ViajeList, registrar_usuario, \
    crear_solicitud, solicitudes_nuevas, solicitudes_eliminadas, cancelar_solicitud, asignar_solicitud, \
    planificar_solicitud, cerrar_solicitud, dar_curso_solicitud
from rest_framework.authtoken import views

urlpatterns = [
    # Register / Login / Users
    path('registrar_usuario/', registrar_usuario, name='alta usuario'),
    path('login/', views.obtain_auth_token, name='login'),

    # Admin Lists
    path('provincias', ProvinciaList.as_view()),
    path('materiales', MaterialList.as_view()),


    # Gestión de solicitudes
    path('crear_solicitud', crear_solicitud),
    path('asignar_solicitud', asignar_solicitud),
    path('planificar_solicitud', planificar_solicitud),
    path('dar_curso_solicitud', dar_curso_solicitud),
    path('cerrar_solicitud', cerrar_solicitud),
    path('cancelar_solicitud', cancelar_solicitud),


    # Listas por Rol
    path('solicitudes_nuevas', solicitudes_nuevas),
    path('solicitudes_eliminadas', solicitudes_eliminadas),
    path('solicitudes', SolicitudList.as_view()),
    path('solicitudes_mensajes', SolicitudMensajeList.as_view()),
    path('viajes', ViajeList.as_view()),
    path('viajes_solicitudes', ViajeSolicitudList.as_view()),




]

