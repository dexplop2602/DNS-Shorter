# test_ionos.py
import os
from dotenv import load_dotenv
import ionoscloud_dns
from ionoscloud_dns.exceptions import ApiException

# Cargar las mismas variables de entorno que usa la app
load_dotenv()
IONOS_PREFIX = os.getenv("IONOS_PREFIX")
IONOS_SECRET = os.getenv("IONOS_SECRET")

print("--- Intentando conectar con la API de IONOS ---")
print(f"Usando Prefijo (Público): {IONOS_PREFIX[:4]}... (longitud: {len(IONOS_PREFIX)})")
print(f"Usando Secreto (Privado): {IONOS_SECRET[:4]}... (longitud: {len(IONOS_SECRET)})")

if not IONOS_PREFIX or not IONOS_SECRET:
    print("\nERROR: IONOS_PREFIX o IONOS_SECRET no se encontraron en el archivo .env. Asegúrate de que el archivo existe y tiene los valores correctos.")
    exit()

try:
    # Configurar el cliente de la misma forma que en la aplicación
    ionos_config = ionoscloud_dns.Configuration(username=IONOS_PREFIX, password=IONOS_SECRET)
    api_client = ionoscloud_dns.ApiClient(configuration=ionos_config)
    zones_api = ionoscloud_dns.api.zones_api.ZonesApi(api_client)

    print("\nConfiguración correcta. Intentando listar zonas DNS...")
    
    # Esta es una llamada simple de solo lectura. Si funciona, las credenciales son válidas.
    zones = zones_api.zones_get()
    
    print("\n¡ÉXITO! La conexión con la API de IONOS funcionó.")
    print(f"Se encontraron {len(zones.items)} zonas DNS en tu cuenta.")
    for zone in zones.items:
        print(f" - Zona: {zone.properties.zone_name} (ID: {zone.id})")

except ApiException as e:
    print("\n¡FALLO! La API de IONOS devolvió un error.")
    print(f"HTTP Status: {e.status}")
    print(f"Razón: {e.reason}")
    print(f"Cuerpo del error: {e.body}")

except Exception as e:
    print(f"\n¡FALLO! Ocurrió un error inesperado de Python: {e}")