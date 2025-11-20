import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DOMAIN = os.getenv("BASE_DOMAIN")
IONOS_PREFIX = os.getenv("IONOS_PREFIX")
IONOS_SECRET = os.getenv("IONOS_SECRET")

PENDING_FILE = "/vagrant/pending_records.json"
SYNCED_FILE = "/vagrant/synced_records.json"
IONOS_API_URL = "https://api.hosting.ionos.com/dns/v1"

def get_api_headers():
    """Construye la cabecera de autenticación X-API-Key correcta."""
    if not IONOS_PREFIX or not IONOS_SECRET:
        return None
    
    # Formato correcto: prefix.secret
    api_key = f"{IONOS_PREFIX}.{IONOS_SECRET}"
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return headers

def load_json_file(filepath):
    if not os.path.exists(filepath): return {}
    with open(filepath, "r") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def save_json_file(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def main():
    print("--- Iniciando Sincronizador de DNS ---")
    
    pending_urls = load_json_file(PENDING_FILE)
    if not pending_urls:
        print("No hay registros pendientes. Saliendo.")
        return

    headers = get_api_headers()
    if not headers:
        print("ERROR: No se pudieron cargar las credenciales.")
        return

    # 1. Obtener el ID de la Zona
    try:
        response = requests.get(f"{IONOS_API_URL}/zones", headers=headers)
        response.raise_for_status()
        zones = response.json()
        zone_id = None
        for zone in zones:
            if zone.get('name') == BASE_DOMAIN:
                zone_id = zone.get('id')
                break
        if not zone_id:
            print(f"ERROR: No se encontró la zona para '{BASE_DOMAIN}'.")
            return
    except requests.exceptions.RequestException as e:
        print(f"ERROR al obtener Zone ID: {e}")
        return

    print(f"Sincronizando {len(pending_urls)} registro(s) para la zona {zone_id}...")
    
    synced_records = load_json_file(SYNCED_FILE)
    records_to_remove_from_pending = []

    for short_code, long_url in pending_urls.items():
        try:
            # --- CORRECCIÓN FINAL ---
            # 1. El 'name' DEBE ser el dominio completo (FQDN).
            # 2. Eliminamos 'prio' (inválido para TXT).
            # 3. El contenido va entre comillas.
            
            full_name = f"{short_code}.{BASE_DOMAIN}"
            
            payload = [
                {
                    "name": full_name,     # <--- CAMBIO CLAVE AQUÍ
                    "type": "TXT",
                    "content": f'"{long_url}"',
                    "ttl": 3600,
                    "disabled": False
                }
            ]
            
            print(f"Enviando registro: {full_name} ...")
            
            response = requests.post(
                f"{IONOS_API_URL}/zones/{zone_id}/records",
                headers=headers,
                json=payload
            )
            
            if response.status_code >= 400:
                print(f"❌ Error {response.status_code}: {response.text}")
                # Si el error es que ya existe, lo marcamos como sincronizado para no bloquear
                if "already exists" in response.text or "DUPLICATE" in response.text:
                    print("   (El registro ya existía, marcando como sincronizado)")
                    records_to_remove_from_pending.append(short_code)
            else:
                print(f"✔️ ¡ÉXITO! Registro creado.")
                synced_records[short_code] = long_url
                records_to_remove_from_pending.append(short_code)

        except requests.exceptions.RequestException as e:
            print(f"❌ Fallo de conexión: {e}")

    # Actualizar archivos locales
    if records_to_remove_from_pending:
        for code in records_to_remove_from_pending:
            if code in pending_urls:
                del pending_urls[code]
        
        save_json_file(PENDING_FILE, pending_urls)
        save_json_file(SYNCED_FILE, synced_records)
        print(f"Sincronización completada. {len(records_to_remove_from_pending)} registros procesados.")

    print("--- Sincronizador finalizado ---")

if __name__ == "__main__":
    main()