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
app = FastAPI(title="Acortador de URLs (Interfaz Web)")
templates = Jinja2Templates(directory="templates")

PENDING_FILE = "/vagrant/pending_records.json"
BASE_DOMAIN = os.getenv("BASE_DOMAIN")

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
    
    short_code = secrets.token_urlsafe(6).lower()
    pending_urls[short_code] = url
    save_json_file(PENDING_FILE, pending_urls)
    
    new_short_url = f"{request.url.scheme}://{request.url.netloc}/{short_code}"
    message = f"¡Éxito! Tu enlace es: <a href='{new_short_url}'>{new_short_url}</a><br><small>(Puede tardar hasta un minuto en activarse)</small>"
    
    return templates.TemplateResponse("index.html", {"request": request, "message": message})

@app.get("/{short_path:path}")
async def resolve_and_redirect(short_path: str):
    if short_path == "favicon.ico": return Response(status_code=204)
    if not BASE_DOMAIN: return Response(content="Error: BASE_DOMAIN no está configurado.", status_code=500)
    
    dns_query_name = f"{short_path}.{BASE_DOMAIN}"
    try:
        answers = dns.resolver.resolve(dns_query_name, 'TXT')
        redirect_url_bytes = answers[0].strings[0]
        redirect_url = redirect_url_bytes.decode('utf-8').strip('"')
        return RedirectResponse(url=redirect_url, status_code=307)
    except dns.exception.DNSException:
        return Response(content=f"El enlace corto '{short_path}' no fue encontrado o aún no está activo.", status_code=404)
    except Exception:
        return Response(content="Error interno del servidor.", status_code=500)