import os
import json
import requests
from dotenv import load_dotenv

# Cargar las mismas variables de entorno
load_dotenv()

BASE_DOMAIN = os.getenv("BASE_DOMAIN")
IONOS_PREFIX = os.getenv("IONOS_PREFIX")
IONOS_SECRET = os.getenv("IONOS_SECRET")

# Archivos para gestionar el estado
PENDING_FILE = "/vagrant/pending_records.json"
SYNCED_FILE = "/vagrant/synced_records.json"

IONOS_API_URL = "https://api.hosting.ionos.com/dns/v1"

def get_api_headers():
    if not IONOS_PREFIX or not IONOS_SECRET:
        return None
    api_key = f"{IONOS_PREFIX}.{IONOS_SECRET}"
    return {"X-API-Key": api_key, "Content-Type": "application/json"}

def load_json_file(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json_file(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def main():
    print("--- Iniciando Sincronizador de DNS ---")
    
    pending_urls = load_json_file(PENDING_FILE)
    if not pending_urls:
        print("No hay registros pendientes para sincronizar. Saliendo.")
        return

    headers = get_api_headers()
    if not headers:
        print("ERROR: No se pudieron cargar las credenciales de la API de IONOS.")
        return

    # Obtener el Zone ID una sola vez
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
            print(f"ERROR: No se encontró la zona para el dominio '{BASE_DOMAIN}'.")
            return
    except requests.exceptions.RequestException as e:
        print(f"ERROR al obtener el Zone ID: {e}")
        return

    print(f"Sincronizando {len(pending_urls)} registro(s) para la zona {zone_id}...")
    
    synced_records = load_json_file(SYNCED_FILE)
    records_to_remove_from_pending = []

    for short_code, long_url in pending_urls.items():
        try:
            payload = {
                "name": short_code,
                "type": "TXT",
                "content": f'"{long_url}"', # El contenido de TXT entre comillas
                "ttl": 3600,
                "prio": 0,
                "disabled": False
            }
            
            print(f"Intentando crear registro para {short_code}...")
            
            response = requests.post(
                f"{IONOS_API_URL}/zones/{zone_id}/records",
                headers=headers,
                json=[payload]
            )
            response.raise_for_status()
            
            print(f"✔️  Éxito al crear el registro para {short_code}.")
            synced_records[short_code] = long_url
            records_to_remove_from_pending.append(short_code)

        except requests.exceptions.RequestException as e:
            error_body = e.response.text if e.response else str(e)
            print(f"❌  FALLO al crear el registro para {short_code}. La API respondió:")
            print(error_body)
            # El registro se quedará en pending para el próximo intento

    # Actualizar los archivos de estado
    if records_to_remove_from_pending:
        for code in records_to_remove_from_pending:
            del pending_urls[code]
        
        save_json_file(PENDING_FILE, pending_urls)
        save_json_file(SYNCED_FILE, synced_records)
        print(f"Se sincronizaron {len(records_to_remove_from_pending)} registros con éxito.")

    print("--- Sincronizador de DNS finalizado ---")

if __name__ == "__main__":
    main()