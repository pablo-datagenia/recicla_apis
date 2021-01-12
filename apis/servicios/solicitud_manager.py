from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.utils.datetime_safe import datetime
from rest_framework import status

from ..decorators import validarGrupo
from ..models import Solicitud, SolicitudEstado, SolicitudMaterial, Material, PuntoRecoleccion


class SolicitudAcciones:
    CREAR = 'Nueva'
    ASIGNAR = 'Asignar'
    PLANIFICAR = 'Planificar'
    CERRAR = 'Cerrar'
    CANCELAR = 'Cancelar'
    ELIMINAR = 'Eliminar'

    ACCIONES = {
        'CREAR': 1,
        'ASIGNAR': 2,
        'PLANIFICAR': 3,
        'CERRAR': 4,
        'CANCELAR': 5,
        'ELIMINAR': 6
    }


class SolicitudManager(object):

    @classmethod
    def __obtener_obj(cls, data_ids):
        try:
            return Solicitud.objects.filter(pk__in=data_ids)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def __obtener_punto(cls, punto_id):
        try:
            return PuntoRecoleccion.objects.get(pk=punto_id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def __tiene_permiso(cls, usuario, accion):
        """
            Persmisos básicos van por decorator, aqui valida permisos especiales
        """

        if accion == SolicitudAcciones.CREAR:
            # Va por decoratos
            return True

        if accion in [SolicitudAcciones.ASIGNAR,
                      SolicitudAcciones.PLANIFICAR,
                      SolicitudAcciones.CERRAR,
                      SolicitudAcciones.CANCELAR]:
            if validarGrupo(usuario, 'recolector') or \
                    validarGrupo(usuario, 'administrador'):
                return True

        if accion == SolicitudAcciones.ELIMINAR:
            # Va por decoratos
            if validarGrupo(usuario, 'administrador'):
                return True

        return False

    @classmethod
    def crear_solicitud(cls, data, usuario):

        if not cls.__tiene_permiso(usuario, SolicitudAcciones.CREAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para crear solicitudes'

        if 'punto' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario sin punto de recolección no puede crear solicitud'

        punto = cls.__obtener_punto(data['punto'])
        if not punto:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario sin punto de recolección no puede crear solicitud'

        if 'materiales' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No informa materiales para crear solicitud'

        try:

            materiales_str = data['materiales']
            materiales_list = materiales_str.split(';')

            solicitud = Solicitud()
            solicitud.usuario = usuario
            solicitud.estado = SolicitudEstado.NUEVA
            solicitud.materiales = materiales_str
            solicitud.punto = punto
            solicitud.comentario = data['comentario']
            solicitud.save()

            for material in materiales_list:
                sm = SolicitudMaterial()
                sm.material = Material.objects.get(codigo=material)
                sm.solicitud = solicitud
                sm.save()

            return status.HTTP_200_OK, {'id': solicitud.pk}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear solicitud {str(ex)}'

    @classmethod
    def __obtener_por_estado(cls, estados, lista=True, usuario=None):

        solicitudes = Solicitud.objects.all().exclude(eliminada=True)
        if usuario:
            solicitudes = solicitudes.filter(usuario=usuario)

        solicitudes = solicitudes.filter(estado__in=estados)

        if lista:
            solicitudes = solicitudes.values('id',
                                             fec=F('creada'),
                                             est=F('estado'),
                                             usu=F('usuario__username'),
                                             punt=F('punto__domicilio'),
                                             mat=F('materiales'))

        return solicitudes

    @classmethod
    def obtener_lista_solicitudes_recolector(cls, data, usuario):

        try:
            solicitudes = cls.__obtener_por_estado(estados=data['estados'], lista=True, usuario=usuario)
            return status.HTTP_200_OK, solicitudes

        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_solicitudes_recolector(cls, data, usuario):

        try:
            solicitudes = cls.__obtener_por_estado(estados=data['estados'], lista=False, usuario=usuario)
            return status.HTTP_200_OK, solicitudes

        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_eliminadas(cls, usuario):
        # Solo para gestion del Administrador
        # los eliminados quedan fuera de Workflow
        try:

            if not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Debe ser administrador'

            eliminadas = Solicitud.objects.filter(eliminada=True).\
                values('id',
                       'creada',
                       fecha_eliminacion=F('modificada'),
                       usu=F('usuario__username'),
                       punt=F('punto__domicilio'),
                       mat=F('materiales'))

            return status.HTTP_200_OK, eliminadas
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def asignar_solicitud(cls, data, usuario):
        # Recolector puede asignarse/desasignarse una o varias solicitudes
        asignar = True

        if 'ids' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede asignar/desasignar solicitud sin su clave'

        if 'des' in data and not data['des']:
            asignar = False

        solis = cls.__obtener_obj(data['ids'])
        if solis is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existen las solicitudes'

        try:
            cantidad = 0
            if asignar:
                for soli in solis:
                    if soli.estado != SolicitudEstado.NUEVA or soli.eliminada:
                        return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                               'No se puede asignar la solicitud estado incorrecto'

                    soli.estado = SolicitudEstado.ASIGNADA
                    soli.recolector = usuario
                    soli.asignada = datetime.now()
                    soli.save()
                    cantidad += 1

                return status.HTTP_200_OK, {'ASIGNADAS': cantidad}

            else:
                for soli in solis:
                    if soli.estado != SolicitudEstado.ASIGNADA or soli.eliminada:
                        return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede desasignar la solicitud'

                    soli.estado = SolicitudEstado.NUEVA
                    soli.recolector = None
                    soli.asignada = None
                    soli.save()
                    cantidad += 1

                return status.HTTP_200_OK, {'DESASIGNADAS': cantidad}

        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def cancelar_solicitud(cls, data, usuario):
        # Puede cancelar una solicitud el mismo usaurio que la creo o el administrador
        if 'ids' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar solicitudes sin su clave'

        solis = cls.__obtener_obj(data['ids'])
        if solis is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existen solicitudes'

        try:
            es_administrador = validarGrupo(usuario, 'administrador')
            cantidad = 0
            for soli in solis:
                if soli.usuario != usuario and not es_administrador:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede cancelar solicitud de otro usuario'

                if soli.estado == SolicitudEstado.CERRADA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar solicitud cerrada o eliminada'

                soli.estado = SolicitudEstado.CANCELADA
                soli.cancelada = datetime.now()
                soli.save()
                cantidad += 1

            return status.HTTP_200_OK, {'CANCELADAS': cantidad}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def planificar_solicitud(cls, data, usuario):

        planificar = True
        if 'ids' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede planificar solicitudes sin claves'

        if 'des' in data and not data['des']:
            planificar = False

        solis = cls.__obtener_obj(data['ids'])
        if solis is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:
            es_administrador = validarGrupo(usuario, 'administrador')
            cantidad = 0
            if planificar:
                for soli in solis:
                    if soli.recolector != usuario and not es_administrador:
                        return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                               'Usuario no puede planificar solicitud de otro usuario'

                    if soli.estado != SolicitudEstado.ASIGNADA or soli.eliminada:
                        return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                               'No se puede planificar solicitud error estado'

                    soli.estado = SolicitudEstado.PLANIFICADA
                    soli.planificada = datetime.now()
                    soli.save()
                    cantidad += 1

                    return status.HTTP_200_OK, {'PLANIFICADAS': cantidad}
            else:  # DES-PLANIFICAR

                for soli in solis:
                    if soli.recolector != usuario and not es_administrador:
                        return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                               'Usuario no puede planificar solicitud de otro usuario'

                    if soli.estado != SolicitudEstado.PLANIFICADA or soli.eliminada:
                        return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                               'No se puede des-planificar solicitud error estado'

                    soli.estado = SolicitudEstado.ASIGNADA
                    soli.planificada = None
                    soli.save()
                    cantidad += 1

                return status.HTTP_200_OK, {'DES-PLANIFICADA': cantidad}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def cerrar_solicitud(cls, data, usuario):

        if 'ids' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cerrar a solicitud sin su clave'

        solis = cls.__obtener_obj(data['ids'])
        if solis is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existen solicitudes'

        try:
            es_administrador = validarGrupo(usuario, 'administrador')
            cantidad = 0
            for soli in solis:
                if soli.recolector != usuario and not es_administrador:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                           'Usuario no puede modificar solicitud de otro recolector'

                if soli.estado not in [SolicitudEstado.EN_VIAJE,
                                       SolicitudEstado.PLANIFICADA,
                                       SolicitudEstado.ASIGNADA] or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                           'No se puede cerrar solicitud que no estuvo en curso, o la misma está eliminada'

                soli.estado = SolicitudEstado.CERRADA
                soli.cerrada = datetime.now()
                soli.save()
                cantidad += 1

            return status.HTTP_200_OK, {'CERRADAS': cantidad}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def eliminar_solicitud(cls, data, usuario):

        if 'ids' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede ELIMINAR solicitudes sin claves'

        solis = cls.__obtener_obj(data['ids'])
        if solis is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existen solicitudes'

        try:
            cantidad = 0
            if not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede eliminar solicitudes'

            for soli in solis:
                soli.eliminada = True
                soli.save()
                cantidad += 1

            return status.HTTP_200_OK, {'ELIMINADAS': cantidad}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def mensajear_solicitud(cls, data, usuario):
        pass
