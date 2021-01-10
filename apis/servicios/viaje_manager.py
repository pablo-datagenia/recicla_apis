from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.utils.datetime_safe import datetime
from rest_framework import status

from .solicitud_manager import SolicitudManager
from ..decorator import validarGrupo
from ..models import Viaje, UsuarioPunto, ViajeEstado, PuntoRecoleccion, SolicitudEstado


class ViajeAcciones:
    INICIAR = 'Asignar'
    CERRAR = 'Cerrar'
    CANCELAR = 'Cancelar'

    ACCIONES = {
        'CREAR': 1,
        'INICIAR': 2,
        'CERRAR': 3,
        'CANCELAR': 4}


class ViajeManager(object):

    @classmethod
    def __obtener_obj(cls, data):
        if 'id' in data:
            try:
                return Viaje.objects.get(pk=data['id'])
            except Viaje.DoesNotExists:
                return None

    @classmethod
    def __obtener_usuario(cls, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExists:
            return None

    @classmethod
    def __obtener_punto(cls, punto_id):
        try:
            return PuntoRecoleccion.objects.get(pk=punto_id)
        except UsuarioPunto.DoesNotExists:
            return None

    @classmethod
    def __tiene_permiso(cls, data, usuario, accion):
        """
            Persmisos básicos van por decorator, aqui valida permisos especiales
        """

        if accion == ViajeAcciones.CREAR:
            # Va por decoratos
            return True

        return False

    @classmethod
    def iniciar_viaje(cls, data, usuario):

        if not cls.__tiene_permiso(data, usuario, ViajeAcciones.INICIAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para crear Viajes'

        try:

            planificadas = SolicitudManager.obtener_planificadas(usuario)
            # TODO:  Revisar esta negativa
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

            return status.HTTP_200_OK, {'id': Viaje.id, 'recolecciones': cantidad}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear Viaje {str(ex)}'

    @classmethod
    def posicion_viaje(cls, data, usuario):

        if not cls.__tiene_permiso(data, usuario, ViajeAcciones.INICIAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para modificar Viajes'

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar Viaje sin su clave'

        if 'posx' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar posicion sin clave'

        if 'posy' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar posicion sin clave'

        try:
            viaje = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:

            viaje.pos_x = data['posx']
            viaje.pos_y = data['posy']
            viaje.save()

            return status.HTTP_200_OK, {'id': viaje.id, 'pos_x': viaje.pos_x, 'pos_y': viaje.pos_y}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear Viaje {str(ex)}'

    @classmethod
    def cerrar_viaje(cls, data, usuario):

        if not cls.__tiene_permiso(data, usuario, ViajeAcciones.INICIAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para modificar Viajes'

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar Viaje sin su clave'

        try:
            viaje = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:

            viaje.estado = ViajeEstado.CERRADO
            viaje.save()

            en_viaje = SolicitudManager.obtener_en_viaje(viaje)

            cantidad = 0
            for soli in en_viaje:
                cantidad += 1
                soli.estado = SolicitudEstado.CERRADA
                soli.cerrada = datetime.now()
                soli.save()

            return status.HTTP_200_OK, {'id': viaje.id, 'estado': 'CERRADO', 'recolecciones': cantidad}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear Viaje {str(ex)}'

    @classmethod
    def cancelar_viaje(cls, data, usuario):

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar Viaje sin su clave'

        try:
            viaje = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:
            if viaje.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede cancelar Viaje de otro usuario'

            viaje.estado = ViajeEstado.CANCELADO
            viaje.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'CANCELADA'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def planificar_Viaje(cls, data, usuario):

        planificar = True

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar Viaje sin su clave'

        if 'des' in data:
            planificar = False

        try:
            soli = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:
            if soli.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede planificar Viaje de otro usuario'

            if planificar:
                if soli.estado != ViajeEstado.ASIGNADA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede planificar Viaje error estado'

                soli.estado = ViajeEstado.PLANIFICADA
                soli.planificada = datetime.now()
                soli.save()

                return status.HTTP_200_OK, {'id': soli.id, 'estado': 'PLANIFICADA'}
            else:  # DES-PLANIFICAR
                if soli.estado != ViajeEstado.PLANIFICADA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede des-planificar Viaje error estado'

                soli.estado = ViajeEstado.ASIGNADA
                soli.planificada = None
                soli.save()

                return status.HTTP_200_OK, {'id': soli.id, 'estado': 'DES-PLANIFICADA'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def dar_curso_Viaje(cls, data, usuario):
        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede dar curso a Viaje sin su clave'

        try:
            soli = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:
            if soli.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no modificar Viaje de otro recolector'

            if soli.estado != ViajeEstado.PLANIFICADA or soli.eliminada:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                       'No se puede dar curso a Viaje en no planificada o eliminada'

            soli.estado = ViajeEstado.EN_CURSO
            soli.en_curso = datetime.now()
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'EN CURSO'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def cerrar_Viaje(cls, data, usuario):

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cerrar a Viaje sin su clave'

        try:
            soli = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:
            if soli.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede modificar Viaje de otro recolector'

            if soli.estado != ViajeEstado.EN_CURSO or soli.eliminada:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                       'No se puede cerrar Viaje que no estuvo en curso, o la misma está eliminada'

            soli.estado = ViajeEstado.CERRADA
            soli.cerrada = datetime.now()
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'CERRADA'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)


    @classmethod
    def eliminar_Viaje(cls, data, usuario):

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede ELIMINAR una Viaje sin su clave'

        try:
            soli = Viaje.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Viaje'

        try:
            if not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede eliminar Viaje'

            soli.eliminada = True
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'ELIMINADA POR ADMIN'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def mensajear_Viaje(cls, data, usuario):
        pass

