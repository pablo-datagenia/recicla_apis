from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.

class Provincia(models.Model):
    provincia = models.CharField(max_length=50, unique=True)
    habilitada = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + '-' + self.provincia


class UsuarioRol(models.Model):
    rol = models.CharField(max_length=50, verbose_name='Rol de aplicación', null=False, blank=False)
    habilitado = models.BooleanField(default=False)
    descripcion = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.pk) + '-' + self.rol


class Usuario(AbstractUserModel):
    usuario = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    rol = models.ForeignKey(UsuarioRol, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return str(self.pk) + '-' + self.usuario


class UsuarioDomicilio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=False)
    domicilio = models.CharField(max_length=250, blank=True, null=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, null=False)
    geox = models.CharField(max_length=50, blank=True, null=True)
    geoy = models.CharField(max_length=50, blank=True, null=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.domicilio


class SolicitudEstado:
    NUEVA = 'Nueva'
    ASIGNADA = 'Asignada'
    PLANIFICADA = 'Planificada'
    EN_CURSO = 'En curso'
    CERRADA = 'Cerrada'
    CANCELADA = 'Cancelada'

    ESTADOS = (
        (1, NUEVA),
        (2, ASIGNADA),
        (3, PLANIFICADA),
        (4, EN_CURSO),
        (5, CERRADA),
        (6, CANCELADA),
    )


class Solicitud(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=False)
    estado = models.IntegerField(choices=SolicitudEstado.ESTADOS)
    comentario = models.CharField(max_length=250, blank=True, null=True)
    eliminado = models.BooleanField(blank=False, default=False)
    creada = models.DateTimeField(verbose_name='Creada', auto_now_add=True)
    modificada = models.DateTimeField(verbose_name='Modificada', auto_now=True, null=True)

    def __str__(self):
        return str(self.id) + self.usuario.usuario + '(' + self.creada + ')'


class SolicitudMensaje(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.PROTECT, null=False)
    mensaje = models.CharField(max_length=250, blank=True, null=True)
    creada = models.DateTimeField(verbose_name='Creada', auto_now_add=True)


class Material(models.Model):
    material = models.CharField(max_length=150, blank=False, null=False)


class SolicitudMaterial(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.PROTECT, null=False)
    material = models.ForeignKey(Material, on_delete=models.PROTECT, null=False)


class Viaje(models.Model):
    creado = models.DateTimeField(verbose_name='Creado', auto_now_add=True)
    inicio = models.DateTimeField(verbose_name='Inicia en', null=True, blank=True)
    fin = models.DateTimeField(verbose_name='Finalizado en', null=True, blank=True)
    recolector = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=False, verbose_name='Recolector')

    def __str__(self):
        return self.recolector + '-Viaje:' + self.pk


class ViajeSolicitud(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.PROTECT, null=False)
    solicitud = models.ForeignKey(Solicitud, on_delete=models.PROTECT, null=False)

