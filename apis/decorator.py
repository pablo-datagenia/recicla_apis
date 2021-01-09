

def validarGrupo(usuario, grupo):
    try:
        grupos = list(usuario.groups.all().values_list('name', flat=True))
        if grupos and (grupo in grupos or 'administrador' in grupos):
            return True
        return False
    except Exception as exc:
        return False


def accion_usuario(function):

    def wrap(request, *args, **kwargs):
        if request.user is not None and validarGrupo(request.user, 'usuarios'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionError("El usuario no tiene permisos para hacer esta accion")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def accion_admin(function):

    def wrap(request, *args, **kwargs):
        if request.user is not None and validarGrupo(request.user, 'administrador'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionError("El usuario no tiene permisos para hacer esta accion")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def accion_recolector(function):

    def wrap(request, *args, **kwargs):
        if request.user is not None and validarGrupo(request.user, 'recolector'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionError("El usuario no tiene permisos para hacer esta accion")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def accion_coordinador(function):

    def wrap(request, *args, **kwargs):
        if request.user is not None and validarGrupo(request.user, 'coordinador'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionError("El usuario no tiene permisos para hacer esta accion")

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap