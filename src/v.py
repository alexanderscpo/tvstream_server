import re


class App:
    def __init__(self):
        self.url = '/tv/24/channel/30'

    def get(self, pattern):
        def get_decorator(func):
            def wrapper(*args, **kwargs):
                url = self.url
                # Comprobar si la URL coincide con el patrón especificado
                match = re.match(pattern, url)
                if match:
                    # Extraer los valores de los grupos del patrón
                    tv_id, channel_id = match.groups()

                    # Pasar los valores de los grupos a la función
                    return func(tv_id, channel_id, *args, **kwargs)
                else:
                    # Si la URL no coincide con el patrón, devolver un error 404
                    return "Error 404: URL no encontrada", 404

            return wrapper

        return get_decorator