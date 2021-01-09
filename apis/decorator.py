

def validarGrupo(usuario, grupo):
    try:
        return usuario.groups.filter(name=grupo).exists()
    except Exception as exc:
        return False


def accion_usuario(function):

    def wrap(request, *args, **kwargs):
        if request.user is not None and validarGrupo(request.user, 'usuario'):
            return True
        return False

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
