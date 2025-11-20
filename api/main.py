import os
import secrets
import json
from fastapi import FastAPI, Response, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

import dns.resolver
import dns.exception

# --- CONFIGURACIÓN ---
load_dotenv()
app = FastAPI(
    title="Acortador de URLs con IONOS DNS",
    description="Versión final que muestra la URL pública del dominio.",
    version="FINAL"
)
templates = Jinja2Templates(directory="templates")

# Archivos de inventario
PENDING_FILE = "/vagrant/pending_records.json"
SYNCED_FILE = "/vagrant/synced_records.json"
BASE_DOMAIN = os.getenv("BASE_DOMAIN")

# --- Funciones de Ayuda ---
def load_json_file(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, "r") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_json_file(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

# --- ENDPOINTS ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten", response_class=HTMLResponse)
async def create_short_link(request: Request, url: str = Form(...)):
    pending_urls = load_json_file(PENDING_FILE)
    synced_urls = load_json_file(SYNCED_FILE)
    
    # 1. Comprobar si ya existe
    # En sincronizados
    for short_code, long_url in synced_urls.items():
        if long_url == url:
            # CAMBIO AQUÍ: Usamos BASE_DOMAIN en lugar de request.url.netloc
            existing_short_url = f"http://{BASE_DOMAIN}/{short_code}"
            message = f"Esta URL ya fue acortada: <a href='{existing_short_url}' target='_blank'>{existing_short_url}</a>"
            return templates.TemplateResponse("index.html", {"request": request, "message": message})
    
    # En pendientes
    for short_code, long_url in pending_urls.items():
        if long_url == url:
            # CAMBIO AQUÍ
            existing_short_url = f"http://{BASE_DOMAIN}/{short_code}"
            message = f"Esta URL ya está en cola: <a href='{existing_short_url}' target='_blank'>{existing_short_url}</a>"
            return templates.TemplateResponse("index.html", {"request": request, "message": message})

    # 2. Crear nuevo
    short_code = secrets.token_urlsafe(6).lower()
    pending_urls[short_code] = url
    save_json_file(PENDING_FILE, pending_urls)
    
    # CAMBIO AQUÍ: Construimos la URL final usando tu dominio
    new_short_url = f"http://{BASE_DOMAIN}/{short_code}"
    
    message = f"¡Éxito! Tu enlace es: <a href='{new_short_url}' target='_blank'>{new_short_url}</a><br><small>(Se está creando el registro DNS en segundo plano)</small>"
    
    return templates.TemplateResponse("index.html", {"request": request, "message": message})

@app.get("/{short_path:path}")
async def resolve_and_redirect(short_path: str):
    if short_path == "favicon.ico": return Response(status_code=204)
    if not BASE_DOMAIN: return Response(content="Error: BASE_DOMAIN no está configurado.", status_code=500)
    
    dns_query_name = f"{short_path}.{BASE_DOMAIN}"
    try:
        # Consultar el DNS público para obtener el destino
        answers = dns.resolver.resolve(dns_query_name, 'TXT')
        redirect_url_bytes = answers[0].strings[0]
        redirect_url = redirect_url_bytes.decode('utf-8').strip('"')
        return RedirectResponse(url=redirect_url, status_code=307)
    except dns.exception.DNSException:
        # Si no está en el DNS público (aún no se propagó), miramos nuestros archivos locales
        # Esto permite que la redirección funcione inmediatamente en local
        all_urls = {**load_json_file(PENDING_FILE), **load_json_file(SYNCED_FILE)}
        if short_path in all_urls:
            return RedirectResponse(url=all_urls[short_path], status_code=307)
            
        return Response(content=f"El enlace corto '{short_path}' no fue encontrado o el DNS aún no se ha propagado.", status_code=404)
    except Exception:
        return Response(content="Error interno del servidor.", status_code=500)