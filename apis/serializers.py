from rest_framework import serializers

from apis.models import Provincia, UsuarioRol, Usuario, UsuarioDomicilio, SolicitudEstado, Solicitud, \
    SolicitudMensaje, Material, SolicitudMaterial, Viaje, ViajeSolicitud


# class PreguntaSerializer(serializers.ModelSerializer):
#     opciones = OpcionSerializer(many=True)
#
#     class Meta:
#         model = Pregunta
#         fields = '__all__'
#         extra_kwargs = {'encuesta': {'required': False}, 'usuario': {'required': False}}
#
#     def get_opciones(self, obj):
#         "obj is a Member instance. Returns list of dicts"""
#         qset = Opciones.objects.filter(pregunta=obj)
#         return [OpcionSerializer(m).data for m in qset]


# class EncuestaSerializer(serializers.ModelSerializer):
#     secciones = SeccionSerializer(many=True)
#
#     class Meta:
#         model = Encuesta
#         # fields = '__all__'
#         fields = ['id', 'nombre', 'anonimo', 'usuario', 'desde', 'hasta', 'estado', 'bloqueado', 'vigente', 'secciones',
#                   'mensaje_inicio', 'mensaje_fin', 'mpf_user_name', 'estilo_cabecera', 'frase']
#         extra_kwargs = {'usuario': {'required': False}}

#
# class EncuestaSimpleSerializer(serializers.ModelSerializer):
#     cantidad_respuestas = serializers.SerializerMethodField()
#     s_fecha_desde = serializers.SerializerMethodField()
#     s_fecha_hasta = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Encuesta
#         fields = '__all__'
#
#     def get_cantidad_respuestas(self, obj):
#         respuestas_cant = RespuestaEncuesta.objects.filter(encuesta=obj).count()
#         return respuestas_cant
#
#     def get_s_fecha_desde(self, obj):
#         if obj.desde is not None:
#             s_fecha = obj.desde.strftime("%d-%m-%Y")
#             return s_fecha
#         return None
#
#     def get_s_fecha_hasta(self, obj):
#         if obj.hasta is not None:
#             s_fecha = obj.hasta.strftime("%d-%m-%Y")
#             return s_fecha
#         return None

class ViajeSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViajeSolicitud
        fields = '__all__'


class ViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Viaje
        fields = '__all__'


class SolicitudMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudMaterial
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class SolicitudMensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudMensaje
        fields = '__all__'


class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = '__all__'


class SolicitudEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudEstado
        fields = '__all__'


class UsuarioDomicilioSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioDomicilio
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRol
        fields = '__all__'


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = '__all__'
