

def validarGrupo(usuario, grupo):
    try:
        grupos = list(usuario.groups.all().values_list('name', flat=True))
        if grupos and (grupo in grupos or 'administrador' in grupos):
            return True
        return False
    except Exception as exc:
        return False