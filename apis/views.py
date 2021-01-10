from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from . import serializers, models
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .decorator import accion_usuario, accion_recolector, accion_admin

from .servicios.solicitud_manager import SolicitudManager
from .servicios.viaje_manager import ViajeManager


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def registrar_usuario(request):

    if 'username' not in request.POST or 'password' not in request.POST:
        return Response('Usuario a crear sin datos válidos')

    username = request.POST.get('username')
    password = request.POST.get('password')

    if User.objects.filter(username=username).exists():
        return Response('Usuario ya existente')

    new_user = User.objects.create_user(username=username)
    new_user.set_password(password)
    new_user.save()
    token, created = Token.objects.get_or_create(user=new_user)

    group = Group.objects.get(name='usuarios')
    new_user.groups.add(group)

    return Response(status=status.HTTP_200_OK, data={'token': token.key})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_usuario
def crear_solicitud(request):

    st, data = SolicitudManager.crear_solicitud(request.data, request.user)

    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_usuario
def cancelar_solicitud(request):

    st, data = SolicitudManager.cancelar_solicitud(request.data, request.user)

    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def solicitudes_nuevas(request):

    st, data = SolicitudManager.obtener_nuevas()
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def solicitudes_asignadas(request):

    st, data = SolicitudManager.obtener_asignadas(request.user)
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def solicitudes_planificadas(request):

    st, data = SolicitudManager.obtener_planificadas(request.user)
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def solicitudes_en_curso(request):

    st, data = SolicitudManager.obtener_en_curso(request.user)
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def solicitudes_cerradas(request):

    st, data = SolicitudManager.obtener_cerradas(request.user)
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_admin
def solicitudes_eliminadas(request):

    st, data = SolicitudManager.obtener_eliminadas()
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_admin
def eliminar_solicitud(request):

    st, data = SolicitudManager.eliminar_solicitud(request.data, request.user)
    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def asignar_solicitud(request):

    st, data = SolicitudManager.asignar_solicitud(request.data, request.user)

    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def planificar_solicitud(request):

    st, data = SolicitudManager.planificar_solicitud(request.data, request.user)

    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def iniciar_viaje(request):

    st, data = ViajeManager.iniciar_viaje(request.data, request.user)

    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def actualizar_viaje(request):

    st, data = ViajeManager.actualizar_viaje(request.data, request.user)

    return Response(status=st, data=data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def cerrar_solicitud(request):

    st, data = SolicitudManager.cerrar_solicitud(request.data, request.user)

    return Response(status=st, data=data)


class UsuariosList(generics.ListAPIView):
    serializer_class = serializers.UsuarioSerializer
    queryset = models.User.objects.all()


class MaterialList(generics.ListAPIView):
    serializer_class = serializers.MaterialSerializer
    queryset = models.Material.objects.all()


class ProvinciaList(generics.ListAPIView):
    serializer_class = serializers.ProvinciaSerializer
    queryset = models.Provincia.objects.all()


class SolicitudList(generics.ListAPIView):
    serializer_class = serializers.SolicitudSerializer
    queryset = models.Solicitud.objects.all()


class PuntosList(generics.ListAPIView):
    serializer_class = serializers.PuntoSerializer
    queryset = models.PuntoRecoleccion.objects.all()


class ViajeList(generics.ListAPIView):
    serializer_class = serializers.ViajeSerializer
    queryset = models.Viaje.objects.all()
