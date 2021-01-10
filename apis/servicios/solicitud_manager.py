from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.utils.datetime_safe import datetime
from rest_framework import status

from ..decorator import validarGrupo
from ..models import Solicitud, UsuarioPunto, SolicitudEstado, SolicitudMaterial, Material, PuntoRecoleccion


class SolicitudAcciones:
    CREAR = 'Nueva'
    ASIGNAR = 'Asignar'
    PLANIFICAR = 'Planificar'
    DAR_CURSO = 'Dar curso'
    CERRAR = 'Cerrar'
    CANCELAR = 'Cancelar'

    ACCIONES = {
        'CREAR': 1,
        'ASIGNAR': 2,
        'PLANIFICAR': 3,
        'DAR_CURSO': 4,
        'CERRAR': 5,
        'CANCELAR': 6}


class SolicitudManager(object):

    @classmethod
    def __obtener_obj(cls, data):
        if 'id' in data:
            try:
                return Solicitud.objects.get(pk=data['id'])
            except Solicitud.DoesNotExists:
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

        if accion == SolicitudAcciones.CREAR:
            # Va por decoratos
            return True

        return False

    @classmethod
    def crear_solicitud(cls, data, usuario):

        if not cls.__tiene_permiso(data, usuario, SolicitudAcciones.CREAR):
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

            return status.HTTP_200_OK, {'id': solicitud.id}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear solicitud {str(ex)}'


    @classmethod
    def obtener_nuevas(cls):

        try:
            nuevas = Solicitud.objects.filter(estado=SolicitudEstado.NUEVA).\
                exclude(eliminada=True).values('id',
                                               fec=F('creada'),
                                               usu=F('usuario__username'),
                                               punt=F('punto__domicilio'),
                                               mat=F('materiales'))

            return status.HTTP_200_OK, nuevas
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_asignadas(cls, usuario):

        try:
            asignadas = Solicitud.objects.filter(estado=SolicitudEstado.ASIGNADA,
                                                 usuario=usuario). \
                exclude(eliminada=True).values('id',
                                               fec=F('creada'),
                                               usu=F('usuario__username'),
                                               punt=F('punto__domicilio'),
                                               mat=F('materiales'))

            return status.HTTP_200_OK, asignadas
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_planificadas(cls, usuario):

        try:
            planificadas = Solicitud.objects.filter(estado=SolicitudEstado.PLANIFICADA,
                                                    usuario=usuario). \
                exclude(eliminada=True).values('id',
                                               fec=F('creada'),
                                               usu=F('usuario__username'),
                                               punt=F('punto__domicilio'),
                                               mat=F('materiales'),
                                               plan=F('fecha_planificada'))

            return status.HTTP_200_OK, planificadas
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_en_viaje(cls, viaje):

        try:
            en_viaje = Solicitud.objects.filter(estado=SolicitudEstado.en_viaje,
                                                viaje=viaje). \
                exclude(eliminada=True)

            return status.HTTP_200_OK, en_viaje
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_cerradas(cls, usuario):

        try:
            cerradas = Solicitud.objects.filter(estado=SolicitudEstado.CERRADA,
                                                usuario=usuario). \
                exclude(eliminada=True).values('id',
                                               fec=F('creada'),
                                               usu=F('usuario__username'),
                                               punt=F('punto__domicilio'),
                                               mat=F('materiales'),
                                               plan=F('fecha_planificada'))

            return status.HTTP_200_OK, cerradas
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def obtener_eliminadas(cls):

        try:
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

        asignar = True

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede asignar/desasignar solicitud sin su clave'

        if 'des' in data:
            asignar = False

        try:
            soli = Solicitud.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:

            if asignar:
                if soli.estado != SolicitudEstado.NUEVA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede asignar la solicitud estado incorrecto'

                soli.estado = SolicitudEstado.ASIGNADA
                soli.recolector = usuario
                soli.asignada = datetime.now()
                soli.save()

                return status.HTTP_200_OK, {'id': soli.id, 'estado': 'ASIGNADA'}

            else:
                if soli.estado != SolicitudEstado.ASIGNADA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede desasignar la solicitud'

                soli.estado = SolicitudEstado.NUEVA
                soli.recolector = None
                soli.asignada = None
                soli.save()

                return status.HTTP_200_OK, {'id': soli.id, 'estado': 'DESASIGNADA'}

        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def cancelar_solicitud(cls, data, usuario):

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar solicitud sin su clave'

        try:
            soli = Solicitud.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:
            if soli.usuario != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede cancelar solicitud de otro usuario'

            if soli.estado == SolicitudEstado.CERRADA or soli.eliminada:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar solicitud cerrada o eliminada'

            soli.estado = SolicitudEstado.CANCELADA
            soli.cancelada = datetime.now()
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'CANCELADA'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def planificar_solicitud(cls, data, usuario):

        planificar = True

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cancelar solicitud sin su clave'

        if 'des' in data:
            planificar = False

        try:
            soli = Solicitud.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:
            if soli.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede planificar solicitud de otro usuario'

            if planificar:
                if soli.estado != SolicitudEstado.ASIGNADA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede planificar solicitud error estado'

                soli.estado = SolicitudEstado.PLANIFICADA
                soli.planificada = datetime.now()
                soli.save()

                return status.HTTP_200_OK, {'id': soli.id, 'estado': 'PLANIFICADA'}
            else:  # DES-PLANIFICAR
                if soli.estado != SolicitudEstado.PLANIFICADA or soli.eliminada:
                    return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede des-planificar solicitud error estado'

                soli.estado = SolicitudEstado.ASIGNADA
                soli.planificada = None
                soli.save()

                return status.HTTP_200_OK, {'id': soli.id, 'estado': 'DES-PLANIFICADA'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def dar_curso_solicitud(cls, data, usuario):
        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede dar curso a solicitud sin su clave'

        try:
            soli = Solicitud.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:
            if soli.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no modificar solicitud de otro recolector'

            if soli.estado != SolicitudEstado.PLANIFICADA or soli.eliminada:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                       'No se puede dar curso a solicitud en no planificada o eliminada'

            soli.estado = SolicitudEstado.en_viaje
            soli.en_viaje = datetime.now()
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'EN CURSO'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def cerrar_solicitud(cls, data, usuario):

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede cerrar a solicitud sin su clave'

        try:
            soli = Solicitud.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:
            if soli.recolector != usuario and not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede modificar solicitud de otro recolector'

            if soli.estado != SolicitudEstado.en_viaje or soli.eliminada:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, \
                       'No se puede cerrar solicitud que no estuvo en curso, o la misma está eliminada'

            soli.estado = SolicitudEstado.CERRADA
            soli.cerrada = datetime.now()
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'CERRADA'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)


    @classmethod
    def eliminar_solicitud(cls, data, usuario):

        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede ELIMINAR una solicitud sin su clave'

        try:
            soli = Solicitud.objects.get(pk=data['id'])
        except ObjectDoesNotExist:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la solicitud'

        try:
            if not validarGrupo(usuario, 'administrador'):
                return status.HTTP_500_INTERNAL_SERVER_ERROR, 'Usuario no puede eliminar solicitud'

            soli.eliminada = True
            soli.save()

            return status.HTTP_200_OK, {'id': soli.id, 'estado': 'ELIMINADA POR ADMIN'}
        except Exception as exc:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)

    @classmethod
    def mensajear_solicitud(cls, data, usuario):
        pass

