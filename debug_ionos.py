import os
import requests
import json
import secrets
from dotenv import load_dotenv

# Cargar variables
load_dotenv()
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
IONOS_PREFIX = os.getenv("IONOS_PREFIX")
IONOS_SECRET = os.getenv("IONOS_SECRET")
IONOS_API_URL = "https://api.hosting.ionos.com/dns/v1"

print("--- INICIO DEL DIAGNÓSTICO ---")
print(f"Dominio Base: {BASE_DOMAIN}")

# Construir la autenticación correcta
api_key = f"{IONOS_PREFIX}.{IONOS_SECRET}"
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# 1. Obtener Zone ID
print("\n1. Buscando Zona DNS...")
try:
    response = requests.get(f"{IONOS_API_URL}/zones", headers=headers)
    if response.status_code != 200:
        print(f"❌ Error de conexión/autenticación: {response.status_code}")
        print(response.text)
        exit()
    
    zones = response.json()
    zone_id = None
    for zone in zones:
        if zone.get('name') == BASE_DOMAIN:
            zone_id = zone.get('id')
            break
    
    if not zone_id:
        print(f"❌ No se encontró la zona para {BASE_DOMAIN}")
        exit()
        
    print(f"✔️ Zone ID encontrado: {zone_id}")

except Exception as e:
    print(f"❌ Excepción: {e}")
    exit()

# 2. Pruebas de formato (Payloads)
url_endpoint = f"{IONOS_API_URL}/zones/{zone_id}/records"
test_code = secrets.token_urlsafe(4).lower()
test_url = "https://example.com"

print("\n2. Probando formatos de creación...")

# INTENTO 1: Formato estándar (Sin prio, solo subdominio)
payload_1 = [
    {
        "name": test_code,
        "type": "TXT",
        "content": f'"{test_url}"',
        "ttl": 3600,
        "disabled": False
    }
]
print(f"\n--- INTENTO 1: Solo subdominio, sin 'prio' ---")
print(f"Payload: {json.dumps(payload_1)}")
resp_1 = requests.post(url_endpoint, headers=headers, json=payload_1)
print(f"Status: {resp_1.status_code}")
print(f"RESPUESTA DEL SERVIDOR: {resp_1.text}")

# INTENTO 2: Con rootName (si el 1 falla)
if resp_1.status_code != 201:
    payload_2 = [
        {
            "name": test_code,
            "rootName": BASE_DOMAIN,
            "type": "TXT",
            "content": f'"{test_url}"',
            "ttl": 3600,
            "disabled": False
        }
    ]
    print(f"\n--- INTENTO 2: Con campo 'rootName' ---")
    print(f"Payload: {json.dumps(payload_2)}")
    resp_2 = requests.post(url_endpoint, headers=headers, json=payload_2)
    print(f"Status: {resp_2.status_code}")
    print(f"RESPUESTA DEL SERVIDOR: {resp_2.text}")

print("\n--- FIN ---")