from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from ..decorators import validarGrupo
from ..models import UsuarioPunto, PuntoEstado, PuntoRecoleccion, Provincia


class PuntoAcciones:
    CREAR = 'Crear'
    MODIFICAR = 'Modificar'
    ELIMINAR = 'Eliminar'

    ACCIONES = {
        'CREAR': 1,
        'MODIFICAR': 2,
        'ELIMINAR': 3
    }


class PuntoRecoleccionManager(object):

    @classmethod
    def __obtener_obj(cls, data_id):
        try:
            return PuntoRecoleccion.objects.get(pk=data_id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def __tiene_permiso(cls, obj, usuario, accion):
        """
            Persmisos básicos van por decorator, aqui valida permisos especiales
        """

        if accion == PuntoAcciones.CREAR:
            # Por ahora todos pueden crear
            return True

        if accion in [PuntoAcciones.MODIFICAR, PuntoAcciones.ELIMINAR]:
            # Solo pueden modificar/eliminar el mismo usuario que la creo
            # o el Administrador de la aplicación
            if obj and obj.usuario == usuario or validarGrupo(usuario, 'administrador'):
                return True

        return False

    @classmethod
    def crear_punto_recoleccion(cls, data, usuario):

        if not cls.__tiene_permiso(data, usuario, PuntoAcciones.CREAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para crear Puntos'

        prov = Provincia.objects.get(pk=2)

        try:

            punto = PuntoRecoleccion()
            punto.domicilio = data['dom']
            punto.provincia = prov
            punto.geox = data['geox']
            punto.geoy = data['geox']
            punto.es_global = data['global']
            punto.creado_por = usuario
            punto.horario = data['horario']
            punto.comentario = data['comentario']
            punto.save()

            usuario_punto = UsuarioPunto()
            usuario_punto.usuario = usuario
            usuario_punto.punto = punto
            usuario_punto.save()

            return status.HTTP_200_OK, {'id': punto.id, 'estado': 'HABILITADO',
                                        'usuario': usuario.username, 'global': punto.es_global}

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al crear Punto de Recolección {str(ex)}'

    @classmethod
    def actualizar_punto(cls, data, usuario):

        inhabilitar = False
        if 'id' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar Punto sin su clave'

        if 'geox' not in data or 'geoy' not in data:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No se puede modificar posicion sin clave'

        if 'inhabilitar' in data:
            inhabilitar = True

        punto = cls.__obtener_obj(data['id'])
        if punto is None:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, 'No existe la Punto'

        if not cls.__tiene_permiso(data, usuario, PuntoAcciones.MODIFICAR):
            return status.HTTP_401_UNAUTHORIZED, 'Usuario sin permiso para modificar este Punto de Recolección'
        try:

            if inhabilitar:
                punto.estado = PuntoEstado.INHABILITADO
                punto.save()

                return status.HTTP_200_OK, {'id': punto.id, 'estado': 'INHABILITADO'}

            else:

                prov = Provincia.objects.get(pk=2)

                punto.domicilio = data['dom']
                punto.provincia = prov
                punto.geox = data['geox']
                punto.geoy = data['geox']
                punto.es_global = data['global']
                punto.horario = data['horario']
                punto.comentario = data['comentario']
                punto.save()

        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, f'Error al modificar Punto de Recolección {str(ex)}'
