from django.contrib.auth.models import User
from rest_framework import status
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
            solicitud.estado = SolicitudEstado.ESTADOS['NUEVA']
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
    def asignar_solicitud(cls, data, usuario):
        pass

    @classmethod
    def planificar_solicitud(cls, data, usuario):
        pass

    @classmethod
    def dar_curso_solicitud(cls, data, usuario):
        pass

    @classmethod
    def cerrar_solicitud(cls, data, usuario):
        pass

    @classmethod
    def eliminar_solicitud(cls, data, usuario):
        pass

    @classmethod
    def mensajear_solicitud(cls, data, usuario):
        pass




class NotificacionElectronicaManager(object):

    ESTADO_ERROR_FISCALIA = 10
    ESTADO_ERROR_ID = 20
    ESTADO_JUZGADO_OK = 40
    ESTADO_ERROR_JUZGADO = 42
    ESTADO_ERROR_CAMARA = 43
    ESTADO_NOTIFICACION_OK = 50
    ESTADO_ERROR_CREANDO_NOTIFICACION = 51
    ESTADO_EXPEDIENTE_ENCONTRADO = 60
    ESTADO_EXPEDIENTE_CREADO = 70
    ESTADO_ERROR_CREANDO_EXPEDIENTE = 71

    @classmethod
    def ingresar_notificacion(cls, noti_json, pjn_api_service, usuario, guardar_json=True):
        noti = bool(noti_json)
        if not noti:
            return 306, '306 - Json Vacio', None

        if noti_json.get('idNotification') and Notificacion.objects.filter(
                idNotification=noti_json.get('idNotification')).exists():
            return 409, '409 - Ya existe una notificación con ese idNotification', None

        noti_temp = noti_aux = cls.__crear_ingreso_notificacion(noti_json, guardar_json)

        try:
            # Agrego validacion por camara
            cls.__validar_camara_pjn(noti_json)

            noti_aux.fiscalia, noti_aux.fiscalia_original = cls._obtener_fiscalias_notificaciones(noti_json)
            noti_aux.save()

            cls.__validar_id_notificacion(noti_json)

            noti_aux.fuero_radicacion, noti_aux.juzgado, noti_aux.secretaria = cls.__obtener_fuero_juz_sec(
                noti_json)
            noti_aux.estado_ingreso_por_pjn = cls.ESTADO_JUZGADO_OK
            noti_aux.save()

            noti_temp = notificacion = cls.__crear_notificacion(noti_aux, noti_json, usuario)
            notificacion.estado_ingreso_por_pjn = cls.ESTADO_NOTIFICACION_OK
            notificacion.save()
            noti_aux.delete()

            notificacion.Expediente, notificacion.Movimiento, es_nuevo = cls.__obtener_o_crear_expendiente(
                pjn_api_service, usuario, notificacion)
            if es_nuevo:
                notificacion.estado_ingreso_por_pjn = cls.ESTADO_EXPEDIENTE_CREADO
            else:
                notificacion.estado_ingreso_por_pjn = cls.ESTADO_EXPEDIENTE_ENCONTRADO
            notificacion.save()

            return 200, 'Notificación incorporada', notificacion.id

        except NotificacionNoValidaException as nex:
            noti_temp.estado_ingreso_por_pjn = nex.codigo
            noti_temp.error = str(nex)
            noti_temp.save()
            if not noti_json.get('idNotification'):
                existe_noti = False
            else:
                existe_noti = cls.__validar_existencia_notificacion(noti_json.get('idNotification'))
            if not existe_noti:
                # Por mas que sea rechazada se genera la notificacion con los campos basicos indicando rechazada=True
                cls.__generar_notificacion_rechazada(noti_json, usuario, noti_aux)
            if nex.rechazar:
                return 306, noti_aux.error, noti_temp.id
            else:
                return 200, 'Notificación incorporada parcialmente', noti_temp.id

    @classmethod
    def __crear_ingreso_notificacion(cls, noti_json, guardar_json):

        pjnid = noti_json.get('idNotification')
        fecha = fecha_primero = timezone.now()
        if pjnid:
            anterior = NotificacionAuxiliar.objects.filter(pjn_idNotification=pjnid).first()
            if anterior:
                fecha_primero = anterior.fecha_primera_recepcion
                anterior.delete()

        fechaDtime = None
        try:
            fechaDtime = datetime.strptime(noti_json.get('fechaNotificacionStr'), '%d/%m/%Y %H:%M:%S')
        except Exception:
            pass

        ingreso_noti = NotificacionAuxiliar.objects.create(
            pjn_idNotification=pjnid,
            estado_ingreso_por_pjn=0,
            error='',
            fecha_recepcion=fecha,
            fecha_primera_recepcion=fecha_primero,
            fechaNotificacionDtime=fechaDtime,
            pjn_mpfPjnApiId=noti_json.get('mpfPjnApiId'),
            pjn_idCamara=noti_json.get('idCamara'),
            pjn_idCedula=noti_json.get('idCedula'),
            pjn_idOficina=noti_json.get('idOficina'),
            pjn_cuitToNotify=noti_json.get('cuitToNotify'),
            pjn_idExpediente=noti_json.get('idExpediente'),
            pjn_anioExpediente=noti_json.get('anioExpediente'),
            pjn_claveExpediente=noti_json.get('claveExpediente'),
            pjn_cuitDestination=noti_json.get('cuitDestination'),
            pjn_codigoDesempenio=noti_json.get('codigoDesempenio'),
            pjn_numeroExpediente=noti_json.get('numeroExpediente'),
            pjn_fechaNotificacion=noti_json.get('fechaNotificacion'),
            pjn_materiaExpediente=noti_json.get('materiaExpediente'),
            pjn_caratulaExpediente=noti_json.get('caratulaExpediente'),
            pjn_numeroSubexpediente=noti_json.get('numeroSubexpediente'),
            pjn_cuitGroupDestination=noti_json.get('cuitGroupDestination'),
            pjn_fechaNotificacionStr=noti_json.get('fechaNotificacionStr'),
            pjn_siglaCamaraExpediente=noti_json.get('siglaCamaraExpediente'),
            pjn_cuitDestinationDescription=noti_json.get('cuitDestinationDescription'),
            pjn_cuitGroupDestinationDescription=noti_json.get('cuitGroupDestinationDescription'),
            fiscalia_id=cls.__obtener_fiscalia_id_por_codigo_desempenio(noti_json.get('codigoDesempenio')),
        )

        if guardar_json:
            ingreso_noti.notificacion_json = noti_json
            ingreso_noti.save()

        return ingreso_noti

    @classmethod
    def _obtener_fiscalias_notificaciones(cls, noti_json):
        if noti_json is None:
            raise NotificacionNoValidaException(
                "No se encontraron datos para procesar.", cls.ESTADO_ERROR_FISCALIA, True)

        if 'codigoDesempenio' not in noti_json or not noti_json['codigoDesempenio']:
            raise NotificacionNoValidaException(
                "La notificación no tiene código de desempeño (codigoDesempenio)", cls.ESTADO_ERROR_FISCALIA, True)

        cod_desempenio = noti_json['codigoDesempenio']

        if cod_desempenio and not cod_desempenio.startswith("TEMPORAL"):
            try:
                fiscalia = Fiscalia.objects.get(Codigo=cod_desempenio)
                return fiscalia, fiscalia
            except Exception:
                raise NotificacionNoValidaException(
                    "No existe la fiscalía con código de desempeño '" + cod_desempenio + "'",
                    cls.ESTADO_ERROR_FISCALIA, True)
        else:
            if 'cuitGroupDestination' not in noti_json or not noti_json['cuitGroupDestination']:
                raise NotificacionNoValidaException("No se pudo obtener cuitGroupDestination",
                                                    cls.ESTADO_ERROR_FISCALIA, True)
            return \
                cls._obtener_fiscalia_por_cuif(noti_json['cuitGroupDestination']), \
                cls._obtener_fiscalia_por_cuif(noti_json['cuitGroupDestination'], True)

    @classmethod
    def _obtener_fiscalia_por_cuif(cls, cuif, original=False):
        if not cuif:
            raise NotificacionNoValidaException("No se pudo obtener la fiscalía (CUIF: vacío).",
                                                cls.ESTADO_ERROR_FISCALIA, True)

        cantidad = len(Fiscalia.objects.filter(CUIF=cuif))

        if cantidad < 1:
            raise NotificacionNoValidaException("No se pudo obtener la fiscalía (CUIF: " + str(cuif) + " ).",
                                                cls.ESTADO_ERROR_FISCALIA, True)
        if cantidad > 1:
            raise NotificacionNoValidaException("Existe más de una fiscalía con CUIF: " + str(cuif) + ".",
                                                cls.ESTADO_ERROR_FISCALIA, True)

        fiscalia = Fiscalia.objects.get(CUIF=cuif)

        if not original and fiscalia.fiscalia_padre:
            return fiscalia.fiscalia_padre
        else:
            return fiscalia

    @classmethod
    def __obtener_fiscalia_id_por_codigo_desempenio(cls, codigo_desempenio):
        fiscalia = Fiscalia.objects.filter(Codigo=codigo_desempenio)
        if fiscalia:
            return fiscalia[0].pk
        return None

    @classmethod
    def __validar_camara_pjn(cls, noti_json):
        if not noti_json.get('idCamara'):
            raise NotificacionNoValidaException("Notificación sin id de camara.", cls.ESTADO_ERROR_CAMARA, True)
        else:
            if noti_json.get('idCamara'):
                pjn_idCamara = ""
                try:
                    pjn_idCamara = noti_json.get('idCamara')
                    Camara.objects.get(id=pjn_idCamara)
                except Exception:
                    raise NotificacionNoValidaException(
                        "No existe la camara con el código '" + str(pjn_idCamara) + "'",
                        cls.ESTADO_ERROR_CAMARA, True)

    @classmethod
    def __validar_id_notificacion(cls, noti_json):
        if not noti_json.get('idNotification'):
            raise NotificacionNoValidaException("Notificación sin id.", cls.ESTADO_ERROR_ID, True)

    @classmethod
    def __obtener_fuero_juz_sec(cls, noti_json):
        try:
            return JuzgadoManager.obtener_fuero_juzgado_secretaria(
                noti_json.get('idOficina'), noti_json.get('idCamara'))
        except Exception as ex:
            raise NotificacionNoValidaException(str(ex), cls.ESTADO_ERROR_JUZGADO, False)

    @classmethod
    def __validar_existencia_notificacion(cls, idNotification):
        if Notificacion.objects.filter(idNotification=idNotification).count() > 0:
            return True
        return False

    @classmethod
    def __generar_notificacion_rechazada(cls, noti_json, usuario, noti_aux=None):

        notificacion = Notificacion()
        notificacion.CreadoAutomatico = True
        notificacion.idNotification = noti_json.get('idNotification')
        notificacion.mpfPjnApiId = noti_json.get('mpfPjnApiId')
        notificacion.idCamara = noti_json.get('idCamara')
        notificacion.idOficina = noti_json.get('idOficina')
        notificacion.idCedula = noti_json.get('idCedula')
        notificacion.fechaNotificacion = noti_json.get('fechaNotificacion')
        if noti_json.get('fechaNotificacionStr'):
            notificacion.fechaNotificacionDtime = datetime.strptime(noti_json.get('fechaNotificacionStr'),
                                                                    '%d/%m/%Y %H:%M:%S')
        notificacion.fechaNotificacionStr = noti_json.get('fechaNotificacionStr')
        notificacion.caratulaExpediente = noti_json.get('caratulaExpediente')
        if noti_json.get('claveExpediente') is None:
            notificacion.claveExpediente = " Vacio "
        notificacion.numeroExpediente = noti_json.get('numeroExpediente')
        notificacion.numeroSubexpediente = noti_json.get('numeroSubexpediente')
        notificacion.anioExpediente = noti_json.get('anioExpediente')
        notificacion.siglaCamaraExpediente = noti_json.get('siglaCamaraExpediente')
        notificacion.cuitDestination = noti_json.get('cuitDestination')
        notificacion.cuitGroupDestination = noti_json.get('cuitGroupDestination')
        notificacion.cuitToNotify = noti_json.get('cuitToNotify')
        notificacion.codigoDesempenio = noti_json.get('codigoDesempenio')
        notificacion.idExpediente = noti_json.get('idExpediente')
        notificacion.usuario = usuario
        notificacion.rechazada = True
        if noti_aux:
            if noti_aux.fiscalia:
                notificacion.Fiscalia = noti_aux.fiscalia
                notificacion.cuif_destino = noti_aux.fiscalia.CUIF
            if noti_aux.fiscalia_original:
                notificacion.cuif_original = noti_aux.fiscalia_original.CUIF
            if noti_aux.fuero_radicacion:
                notificacion.Fuero = noti_aux.fuero_radicacion
            if noti_aux.juzgado:
                notificacion.juzgado = noti_aux.juzgado
            if noti_aux.secretaria:
                notificacion.secretaria = noti_aux.secretaria
            if noti_aux.fecha_recepcion:
                notificacion.fecha_recepcion = noti_aux.fecha_recepcion
            if noti_aux.fecha_primera_recepcion:
                notificacion.fecha_primera_recepcion = noti_aux.fecha_primera_recepcion

        notificacion.save()
        return notificacion

    @classmethod
    def __obtener_prop(cls, obj, clave):
        if obj.get(clave) is None:
            raise NotificacionNoValidaException(
                f"No se pudo encontrar la propiedad '{clave}' desde los datos enviados por PJN.",
                cls.ESTADO_ERROR_CREANDO_NOTIFICACION, False)
        return obj.get(clave)

    @classmethod
    def __crear_notificacion(cls, noti_aux, noti_json, usuario):

        notificacion = Notificacion()
        notificacion.CreadoAutomatico = True
        notificacion.idNotification = cls.__obtener_prop(noti_json, 'idNotification')
        notificacion.mpfPjnApiId = cls.__obtener_prop(noti_json, 'mpfPjnApiId')
        notificacion.idCamara = cls.__obtener_prop(noti_json, 'idCamara')
        notificacion.idOficina = cls.__obtener_prop(noti_json, 'idOficina')
        notificacion.idCedula = cls.__obtener_prop(noti_json, 'idCedula')
        notificacion.fechaNotificacion = cls.__obtener_prop(noti_json, 'fechaNotificacion')
        notificacion.fechaNotificacionDtime = datetime.strptime(
            cls.__obtener_prop(noti_json, 'fechaNotificacionStr'), '%d/%m/%Y %H:%M:%S')
        notificacion.fechaNotificacionStr = cls.__obtener_prop(noti_json, 'fechaNotificacionStr')
        notificacion.caratulaExpediente = cls.__obtener_prop(noti_json, 'caratulaExpediente')
        notificacion.claveExpediente = cls.__obtener_prop(noti_json, 'claveExpediente')
        notificacion.numeroExpediente = cls.__obtener_prop(noti_json, 'numeroExpediente')
        notificacion.numeroSubexpediente = cls.__obtener_prop(noti_json, 'numeroSubexpediente')
        notificacion.anioExpediente = cls.__obtener_prop(noti_json, 'anioExpediente')
        notificacion.siglaCamaraExpediente = cls.__obtener_prop(noti_json, 'siglaCamaraExpediente')
        notificacion.cuitDestination = cls.__obtener_prop(noti_json, 'cuitDestination')
        notificacion.cuitGroupDestination = cls.__obtener_prop(noti_json, 'cuitGroupDestination')
        notificacion.cuitToNotify = cls.__obtener_prop(noti_json, 'cuitToNotify')
        notificacion.codigoDesempenio = cls.__obtener_prop(noti_json, 'codigoDesempenio')
        notificacion.idExpediente = cls.__obtener_prop(noti_json, 'idExpediente')
        notificacion.Fiscalia = noti_aux.fiscalia
        notificacion.cuif_original = noti_aux.fiscalia_original.CUIF
        notificacion.cuif_destino = noti_aux.fiscalia.CUIF
        notificacion.Fuero = noti_aux.fuero_radicacion
        notificacion.juzgado = noti_aux.juzgado
        notificacion.secretaria = noti_aux.secretaria
        notificacion.fecha_recepcion = noti_aux.fecha_recepcion
        notificacion.fecha_primera_recepcion = noti_aux.fecha_primera_recepcion
        notificacion.usuario = usuario
        notificacion.save()

        return notificacion

    @classmethod
    def __obtener_o_crear_expendiente(cls, pjn_api_service, usuario, notificacion):

        try:
            cuif = notificacion.cuitGroupDestination
            cuit_usuario = notificacion.cuitDestination

            if existe_expediente_id_pjn(notificacion.idExpediente):
                expediente_es_nuevo = False
                expediente = get_expediente_id_pjn(notificacion.idExpediente)

            else:
                pjn_api_service.actualizar_datos_usuario(str(cuif), str(cuit_usuario))
                exp_pjn, status = pjn_api_service.get_expedientes_by_id(notificacion.idExpediente)

                if status != 200:
                    raise NotificacionNoValidaException(
                        f"No se pudieron obtener los datos desde PJN para el expediente (Error {status}).",
                        cls.ESTADO_ERROR_CREANDO_EXPEDIENTE, False)

                fuero, numero, anio, incidente = parsear_clave_expediente(exp_pjn['clave'])
                if existe_expediente(anio, numero, fuero, incidente):
                    expediente_es_nuevo = False
                    expediente = get_expediente(anio, numero, fuero, incidente)
                    expediente.id_pjn = notificacion.idExpediente
                    if expediente.cuif_pjn is None:
                        expediente.cuif_pjn = cuif
                else:
                    expediente_es_nuevo = True
                    expediente = Expediente()
                    expediente.id_pjn = notificacion.idExpediente
                    expediente.FueroCodigo = fuero
                    expediente.Caratula = exp_pjn['caratula']
                    expediente.Numero = numero
                    expediente.Anio = anio
                    expediente.NumeroIncidente = incidente
                    expediente.Fuero = notificacion.Fuero
                    expediente.Fiscalia = notificacion.Fiscalia
                    expediente.Juzgado = notificacion.juzgado
                    expediente.Secretaria = notificacion.secretaria
                    expediente.cuif_pjn = cuif

            expediente.save()
            expediente.FiscaliasVista.add(notificacion.Fiscalia)

            movimiento = Movimiento()
            movimiento.Expediente = expediente
            movimiento.Fiscalia = notificacion.Fiscalia
            movimiento.TipoEntrada = TipoEntrada.objects.get(pk=tipo_entrada_enum.Notificacion)
            movimiento.Tipo = 'NOTIFICACION_ELECTRONICA'
            expediente.TipoUltimoMovimiento = 'NOTIFICACION_ELECTRONICA'
            movimiento.Juzgado = notificacion.juzgado
            movimiento.Secretaria = notificacion.secretaria
            movimiento.UserLog = usuario
            movimiento.save()
            movimiento.TiposNotificacion.set(list(TipoNotificacion.objects.filter(Descripcion='No consta')))

            return expediente, movimiento, expediente_es_nuevo

        except Exception as ex:
            raise NotificacionNoValidaException(f"No se pudo crear el expediente ({str(ex)}).",
                                                cls.ESTADO_ERROR_CREANDO_EXPEDIENTE, False)

