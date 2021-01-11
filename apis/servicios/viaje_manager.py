from django.core.exceptions import ObjectDoesNotExist
from django.utils.datetime_safe import datetime
from rest_framework import status

from .solicitud_manager import SolicitudManager
from ..decorator import validarGrupo
from ..models import Viaje, ViajeEstado, SolicitudEstado


class ViajeAcciones:
    INICIAR = 'Asignar'
    FINALIZAR = 'Finalizar'
    CANCELAR = 'Cancelar'

    ACCIONES = {
        'INICIAR': 1,
        'FINALIZAR': 2,
        'CANCELAR': 3}


class ViajeManager(object):

    @classmethod
    def __obtener_obj(cls, data_id):
        try:
            return Viaje.objects.get(pk=data_id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def __tiene_permiso(cls, data, usuario, accion):
        """
            Persmisos básicos van por decorator, aqui valida permisos especiales
        """

        if accion == ViajeAcciones.INICIAR:
            if validarGrupo(usuario, 'recolector') or validarGrupo(usuario, 'administrador'):
                return True

        if accion in [ViajeAcciones.CANCELAR,
                      ViajeAcciones.FINALIZAR]:
            if (validarGrupo(usuario, 'recolector') and data.recolector == usuario) \
                    or validarGrupo(usuario, 'administrador'):
                return True

        return False

    @classmethod
    def iniciar_viaje(cls, data, usuario):

        if not cls.__tiene_permiso(data, usuario, ViajeAcciones.INICIAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para crear Viajes'

        try:

            planificadas = SolicitudManager.obtener_solicitudes_recolector(data={'estados': ['planificada']},
                                                                           usuario=usuario)
            if not planificadas:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                       'Recolector no puede iniciar viaje sin solicitudes planificadas'

            viaje = Viaje()
            viaje.estado = ViajeEstado.INICIADO
            viaje.recolector = usuario
            viaje.save()

            cantidad = 0
            for soli in planificadas:
                soli.viaje = viaje
                soli.en_viaje = datetime.now()
                soli.save()
                cantidad += 1

            return status.HTTP_200_OK, {'id': viaje.pk, 'recolecciones': cantidad}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear Viaje {str(ex)}'

    @classmethod
    def actualizar_viaje(cls, data, usuario):

        finalizar = False

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar Viaje sin su clave'

        if 'posx' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar posicion sin clave'

        if 'posy' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar posicion sin clave'

        if 'fin' in data and data['fin']:
            finalizar = True

        viaje = cls.__obtener_obj(data['id'])
        if viaje is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe el Viaje'

        if not cls.__tiene_permiso(viaje, usuario, ViajeAcciones.FINALIZAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para modificar Viajes'

        try:

            viaje.pos_x = data['posx']
            viaje.pos_y = data['posy']
            cantidad = 0
            if finalizar:
                viaje.estado = ViajeEstado.CERRADO
                viaje.fin = datetime.now()
                en_viaje = SolicitudManager.obtener_solicitudes_recolector(data={'estados': ['en_viaje']},
                                                                           usuario=usuario)
                for soli in en_viaje:
                    cantidad += 1
                    soli.estado = SolicitudEstado.CERRADA
                    soli.cerrada = datetime.now()
                    soli.save()
            viaje.save()

            return status.HTTP_200_OK, {'id': viaje.id, 'pos_x': viaje.pos_x, 'pos_y': viaje.pos_y,
                                        'finalizado': finalizar, 'solicitudes': cantidad}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear Viaje {str(ex)}'

    @classmethod
    def cancelar_viaje(cls, data, usuario):

        if 'ids' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar Viaje sin su clave'

        viaje = cls.__obtener_obj(data['id'])
        if viaje is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe Viaje'

        if not cls.__tiene_permiso(viaje, usuario, ViajeAcciones.FINALIZAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para modificar Viajes'

        try:
            cantidad = 0
            if viaje.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede cancelar Viaje de otro usuario'

            viaje.estado = ViajeEstado.CANCELADO
            viaje.save()
            en_viaje = SolicitudManager.obtener_solicitudes_recolector(data={'estados': ['en_viaje']},
                                                                       usuario=usuario)
            for soli in en_viaje:
                soli.estado = SolicitudEstado.ASIGNADA
                soli.en_viaje = None
                soli.save()
                cantidad += 1

            return status.HTTP_200_OK, {'CANCELADOS': cantidad}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)
