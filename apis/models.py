from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Perfil:
    USUARIO = 'Recicla'
    RECOLECTOR = 'Recolecta'
    CENTRO = 'Organiza'
    COORDINADOR = 'Coordina'
    ADMIN = 'Supervisa'

    PERFILES = (
        (1, USUARIO),
        (2, RECOLECTOR),
        (3, CENTRO),
        (4, COORDINADOR),
        (5, ADMIN),
    )


class Provincia(models.Model):
    objects = models.Manager()

    provincia = models.CharField(max_length=50, unique=True)
    habilitada = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + '-' + self.provincia


class PuntoRecoleccion(models.Model):
    objects = models.Manager()

    domicilio = models.CharField(max_length=250, blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, null=False)
    geox = models.CharField(max_length=50, blank=True, null=True)
    geoy = models.CharField(max_length=50, blank=True, null=True)
    es_global = models.BooleanField(default=False)
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    creada_en = models.DateTimeField(verbose_name='Creada', auto_now_add=True)
    horario = models.CharField(max_length=150, blank=True, null=True)
    comentario = models.CharField(max_length=150, blank=True, null=True)
    estado = models.IntegerField(null=False, default=1)

    def __str__(self):
        return self.domicilio


class UsuarioPunto(models.Model):
    objects = models.Manager()

    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    punto = models.ForeignKey(PuntoRecoleccion, on_delete=models.PROTECT, null=False)
    default = models.BooleanField(default=False)


class PuntoEstado:
    HABILITADO = 1
    INHABILITADO = 2


class SolicitudEstado:
    NUEVA = 1
    ASIGNADA = 2
    PLANIFICADA = 3
    EN_VIAJE = 4
    CERRADA = 5
    CANCELADA = 6


class ViajeEstado:
    NUEVO = 1
    INICIADO = 2
    CERRADO = 3
    CANCELADO = 4


class Viaje(models.Model):
    objects = models.Manager()

    creado = models.DateTimeField(verbose_name='Creado', auto_now_add=True)
    inicio = models.DateTimeField(verbose_name='Inicia en', null=True, blank=True)
    fin = models.DateTimeField(verbose_name='Finalizado en', null=True, blank=True)
    pos_x = models.CharField(max_length=150, verbose_name='coordenadas x', blank=True, null=True)
    pos_y = models.CharField(max_length=150, verbose_name='coordenadas x', blank=True, null=True)
    recolector = models.ForeignKey(User, on_delete=models.PROTECT, null=False, verbose_name='Recolector')
    modificado = models.DateTimeField(verbose_name='Modificado', auto_now=True, null=True, blank=True)
    estado = models.IntegerField(null=False, default=1)

    def __str__(self):
        return self.recolector.username + '-Viaje:' + str(self.pk)


class Solicitud(models.Model):
    objects = models.Manager()

    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=False, related_name='usuario')
    punto = models.ForeignKey(PuntoRecoleccion, on_delete=models.PROTECT, null=True)
    estado = models.IntegerField(null=False, default=1)
    materiales = models.CharField(max_length=250, blank=False, null=False)
    comentario = models.CharField(max_length=250, blank=True, null=True)
    recolector = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='recolector')
    eliminada = models.BooleanField(blank=False, default=False)
    creada = models.DateTimeField(verbose_name='Creada', auto_now_add=True)
    modificada = models.DateTimeField(verbose_name='Modificada', auto_now=True, null=True)
    asignada = models.DateTimeField(verbose_name='Asignada', null=True, blank=True)
    cancelada = models.DateTimeField(verbose_name='Cancelada', null=True, blank=True)
    planificada = models.DateTimeField(verbose_name='Planificada', null=True, blank=True)
    en_viaje = models.DateTimeField(verbose_name='En curso', null=True, blank=True)
    cerrada = models.DateTimeField(verbose_name='Cerrada', null=True, blank=True)
    fecha_planificada = models.DateTimeField(verbose_name=u'Fecha de recolección planificada', null=True, blank=True)
    viaje = models.ForeignKey(Viaje, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return str(self.pk) + '-' + self.usuario.username


class SolicitudMensaje(models.Model):
    objects = models.Manager()

    solicitud = models.ForeignKey(Solicitud, on_delete=models.PROTECT, null=False)
    mensaje = models.CharField(max_length=250, blank=True, null=True)
    creada = models.DateTimeField(verbose_name='Creada', auto_now_add=True)


class Material(models.Model):
    objects = models.Manager()

    material = models.CharField(max_length=150, blank=False, null=False, unique=True)
    codigo = models.CharField(max_length=2, blank=False, null=False, unique=True)

    def __str__(self):
        return str(self.codigo) + '-(' + str(self.material) + ')'


class SolicitudMaterial(models.Model):
    objects = models.Manager()

    solicitud = models.ForeignKey(Solicitud, on_delete=models.PROTECT, null=False)
    material = models.ForeignKey(Material, on_delete=models.PROTECT, null=True)
