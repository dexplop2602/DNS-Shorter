import os
import secrets
import json
from fastapi import FastAPI, Response, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

import dns.resolver
import dns.exception

# --- CONFIGURACIÓN ---
load_dotenv()
app = FastAPI(
    title="IONOS DNS Shortener Pro",
    description="Acortador de URLs profesional con backend DNS.",
    version="FINAL-PRO"
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

# CORRECCIÓN DEL ERROR: Si alguien intenta ir a /shorten manualmente, lo mandamos al inicio
@app.get("/shorten")
async def redirect_shorten_to_root():
    return RedirectResponse(url="/")

@app.post("/shorten")
async def create_short_link(url: str = Form(...)):
    """
    Ahora este endpoint devuelve JSON para que el frontend sea dinámico y no recargue.
    """
    pending_urls = load_json_file(PENDING_FILE)
    synced_urls = load_json_file(SYNCED_FILE)
    
    # 1. Comprobar si ya existe
    # En sincronizados
    for short_code, long_url in synced_urls.items():
        if long_url == url:
            return JSONResponse({
                "status": "exists",
                "short_url": f"http://{BASE_DOMAIN}:8000/{short_code}",
                "original_url": url
            })
    
    # En pendientes
    for short_code, long_url in pending_urls.items():
        if long_url == url:
            return JSONResponse({
                "status": "pending",
                "short_url": f"http://{BASE_DOMAIN}:8000/{short_code}",
                "original_url": url
            })

    # 2. Crear nuevo
    short_code = secrets.token_urlsafe(4).lower() # 4 caracteres es más elegante
    pending_urls[short_code] = url
    save_json_file(PENDING_FILE, pending_urls)
    
    final_url = f"http://{BASE_DOMAIN}:8000/{short_code}"
    
    return JSONResponse({
        "status": "created",
        "short_url": final_url,
        "original_url": url
    })

@app.get("/{short_path:path}")
async def resolve_and_redirect(short_path: str):
    if short_path == "favicon.ico": return Response(status_code=204)
    
    # Protección extra por si acaso
    if short_path == "shorten": return RedirectResponse(url="/")

    if not BASE_DOMAIN: return Response(content="Error: BASE_DOMAIN no está configurado.", status_code=500)
    
    dns_query_name = f"{short_path}.{BASE_DOMAIN}"
    
    try:
        # 1. Intentar resolver DNS público
        answers = dns.resolver.resolve(dns_query_name, 'TXT')
        redirect_url_bytes = answers[0].strings[0]
        redirect_url = redirect_url_bytes.decode('utf-8').strip('"')
        return RedirectResponse(url=redirect_url, status_code=307)
    except dns.exception.DNSException:
        # 2. Fallback local (para que funcione al instante)
        all_urls = {**load_json_file(PENDING_FILE), **load_json_file(SYNCED_FILE)}
        if short_path in all_urls:
            return RedirectResponse(url=all_urls[short_path], status_code=307)
            
        # Página de error 404 bonita
        return HTMLResponse(content=f"""
        <html>
            <head><title>Enlace no encontrado</title></head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px; color: #333;">
                <h1>⚠️ Enlace no encontrado</h1>
                <p>El código <strong>{short_path}</strong> no existe o el DNS aún no se ha propagado.</p>
                <a href="/">Volver al inicio</a>
            </body>
        </html>
        """, status_code=404)
    except Exception:
        return Response(content="Error interno del servidor.", status_code=500)