from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import ProvinciaList, SolicitudList, MaterialList, ViajeList, registrar_usuario, \
    crear_solicitud, solicitudes_nuevas, solicitudes_eliminadas, cancelar_solicitud, asignar_solicitud, \
    planificar_solicitud, cerrar_solicitud, dar_curso_solicitud, PuntosList, eliminar_solicitud, UsuariosList, \
    solicitudes_planificadas, solicitudes_asignadas, solicitudes_en_curso, solicitudes_cerradas
from rest_framework.authtoken import views

urlpatterns = [
    # Register / Login / Users
    path('registrar_usuario/', registrar_usuario, name='alta usuario'),
    path('login/', views.obtain_auth_token, name='login'),
    # Gestión de solicitudes
    path('crear_solicitud', crear_solicitud),
    path('asignar_solicitud', asignar_solicitud),  # y desasignar
    path('planificar_solicitud', planificar_solicitud),  # y sacar de plan representa un viaje de recolección
    path('dar_curso_solicitud', dar_curso_solicitud),
    path('cerrar_solicitud', cerrar_solicitud),
    path('cancelar_solicitud', cancelar_solicitud),
    # Listas por Rol
    path('solicitudes_nuevas', solicitudes_nuevas),
    path('solicitudes_asignadas', solicitudes_asignadas),
    path('solicitudes_planificadas', solicitudes_planificadas),
    path('solicitudes_en_curso', solicitudes_en_curso),
    path('solicitudes_cerradas', solicitudes_cerradas),

    # Admin Lists
    path('usuarios', login_required(UsuariosList.as_view())),
    path('provincias', login_required(ProvinciaList.as_view())),
    path('materiales', login_required(MaterialList.as_view())),
    path('solicitudes', login_required(SolicitudList.as_view())),
    path('puntos', login_required(PuntosList.as_view())),
    path('viajes', login_required(ViajeList.as_view())),

    # Solo por Admin
    path('eliminar_solicitud', eliminar_solicitud),
    path('solicitudes_eliminadas', solicitudes_eliminadas),

]
