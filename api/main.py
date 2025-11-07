import os
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import dns.resolver
import dns.exception

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="DNS URL Shortener",
    description="Un acortador de URLs que utiliza registros TXT de DNS para las redirecciones.",
    version="1.0.0"
)

# Obtener el dominio base desde las variables de entorno
BASE_DOMAIN = os.getenv("BASE_DOMAIN")

@app.get("/{short_path}")
def resolve_and_redirect(short_path: str):
    """
    Recibe una ruta corta, busca el registro TXT correspondiente en el DNS
    y redirige a la URL encontrada.
    """
    if not BASE_DOMAIN:
        return Response(content="Error: La variable de entorno BASE_DOMAIN no está configurada.", status_code=500)

    # Construir el nombre de dominio completo para la consulta DNS
    # ej: test.tu-dominio.com
    dns_query_name = f"{short_path}.{BASE_DOMAIN}"

    try:
        # Realizar la consulta DNS para obtener los registros TXT
        answers = dns.resolver.resolve(dns_query_name, 'TXT')
        
        # Extraer la URL del primer registro TXT encontrado
        # Los registros TXT a menudo vienen entre comillas, así que las quitamos
        redirect_url = answers[0].to_text().strip('"')

        # Devolver una redirección temporal (307) a la URL de destino
        print(f"Redirigiendo '{dns_query_name}' a '{redirect_url}'")
        return RedirectResponse(url=redirect_url, status_code=307)

    except dns.resolver.NXDOMAIN:
        # El subdominio no existe
        print(f"Error: No se encontró el dominio '{dns_query_name}'")
        return Response(content=f"El enlace corto '{short_path}' no fue encontrado.", status_code=404)
        
    except dns.resolver.NoAnswer:
        # El subdominio existe pero no tiene un registro TXT
        print(f"Error: No se encontró un registro TXT para '{dns_query_name}'")
        return Response(content=f"El enlace corto '{short_path}' existe pero no tiene un destino configurado.", status_code=404)

    except Exception as e:
        # Capturar cualquier otro error inesperado
        print(f"Ha ocurrido un error inesperado: {e}")
        return Response(content="Ha ocurrido un error interno en el servidor.", status_code=500)

@app.get("/")
def root():
    """
    Página de inicio que provee información básica.
    """
    return {
        "message": "Bienvenido al Acortador de URLs por DNS.",
        "usage": f"Crea un registro TXT en tu DNS para un subdominio (ej: 'test.{BASE_DOMAIN}') con la URL de destino como valor. Luego, visita http://localhost/{'test'} para ser redirigido."
    }