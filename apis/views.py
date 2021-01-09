from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from . import serializers, models
from .models import Solicitud, SolicitudEstado
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password

from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .decorator import accion_usuario, accion_recolector

from .servicios.solicitud_manager import SolicitudManager


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
def solicitudes_pendientes(request):

    pendientes = Solicitud.objects.filter(estado=SolicitudEstado.NUEVA,
                                          eliminado=False).\
        values('id', 'usuario__username', 'domicilio__domicilio', 'comentario').\
        prefetch_related('usuario', 'domicilio', '')


    return Response()


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@accion_recolector
def asignar_solicitud(request):

    return Response()


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cerrar_solicitud(request):

    return Response()


class ApiUsuario(APIView):
    """
    Lista de usuarios de la aplicación
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):

        token_user = request.user
        if token_user != 'admin':
            return Response('Permiso denegado')

        usuario = self.get_object(pk=pk)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

    def get_object(self, pk):
        try:
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            raise Http404

    # def post(self, request, format=None):
    #     serializer = UsuarioSerializer(data=request.data)
    #     if serializer.is_valid():
    #         # Validar alta de usuario
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProvinciaList(generics.ListAPIView):
    serializer_class = serializers.ProvinciaSerializer
    queryset = models.Provincia.objects.all()


class SolicitudList(generics.ListAPIView):
    serializer_class = serializers.SolicitudSerializer
    queryset = models.Solicitud.objects.all()


class SolicitudMensajeList(generics.ListAPIView):
    serializer_class = serializers.SolicitudMensajeSerializer
    queryset = models.SolicitudMensaje.objects.all()


class MaterialList(generics.ListAPIView):
    serializer_class = serializers.MaterialSerializer
    queryset = models.Material.objects.all()


class ViajeList(generics.ListAPIView):
    serializer_class = serializers.ViajeSerializer
    queryset = models.Viaje.objects.all()


class ViajeSolicitudList(generics.ListAPIView):
    serializer_class = serializers.ViajeSolicitudSerializer
    queryset = models.ViajeSolicitud.objects.all()

