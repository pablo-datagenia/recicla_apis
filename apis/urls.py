from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import ProvinciaList, SolicitudList, MaterialList, ViajeList, registrar_usuario, \
    crear_solicitud, solicitudes_recolector, solicitudes_eliminadas, asignar_solicitud, \
    planificar_solicitud, iniciar_viaje, PuntosList, eliminar_solicitud, UsuariosList, \
    actualizar_viaje, cerrar_solicitud, \
    crear_punto_recoleccion, actualizar_punto_recoleccion, solicitudes_recolector
from rest_framework.authtoken import views

urlpatterns = [
    # Register / Login / Users
    path('registrar_usuario/', registrar_usuario, name='alta usuario'),
    path('login/', views.obtain_auth_token, name='login'),
    # ---  USUARIO
    # Configuración de cuenta sin un punto de recolección no podrá dar de alta solicitudes
    path('crear_punto_recoleccion', crear_punto_recoleccion),
    # Actualizar horario, comentario, coordenadas etc
    path('actualizar_punto_recoleccion', actualizar_punto_recoleccion),
    # Gestión de solicitudes
    # Usuario solicita que se recolecte material de un punto de recolección(domicilio)
    path('crear_solicitud', crear_solicitud),
    # ---  RECOLECTOR
    # Ve las solicitudes nuevas y se asigna las que le queden bien
    path('asignar_solicitud', asignar_solicitud),  # y desasignar si se equivoca
    # Recolector marca a una solicitud como a recolectarse en el próximo viaje
    # puede agregar fecha de recolección y "des-planificar" si lo requiere
    path('planificar_solicitud', planificar_solicitud),
    # Recolector inicia el recorrido para recoger lo planificado
    # se asocia el listado de solicitudes planificadas al viaje
    path('iniciar_viaje', iniciar_viaje),
    # Se actualiza posición del recolector o el estado del viaje (cerrado)
    path('actualizar_viaje', actualizar_viaje),
    # Recolector puede cerrar una solicitud como ya resuelta sin que este en viaje
    path('cerrar_solicitud', cerrar_solicitud),

    # Listas para Pantallas según Rol
    # Recolector ve solicitudes nuevas para Asignarse las que quiera
    # Colores distintivos:

    path('solicitudes_recolector', solicitudes_recolector),
    # -- BLANCO: Nuevas
    # -- AMARILLO: Asignadas
    # -- VERDE: Planificadas o en curso
    # -- NEGRO: Cerradas

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
