# Acortador de URLs con DNS

Este proyecto implementa un servicio para acortar URLs utilizando registros DNS de tipo TXT como base de datos, siguiendo la metodología descrita en el documento PDF.

## Requisitos

- [Vagrant](https://www.vagrantup.com/downloads)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) (o cualquier otro proveedor de Vagrant)
- Un nombre de dominio gestionado en IONOS.

## Puesta en Marcha

1.  **Clonar el repositorio:**
    git clone <tu-repositorio>
    cd <nombre-del-proyecto>

2.  **Configurar el dominio:**
    -   Crea una copia del archivo `.env.example` y renómbralo a `.env`.
    -   Edita el archivo `.env` y establece tu dominio base:
        BASE_DOMAIN=tu-dominio.com

3.  **Crear un enlace corto en IONOS:**
    -   Ve al panel de control de DNS de tu dominio en IONOS.
    -   Crea un nuevo registro `TXT`.
    -   **Host**: `test` (o cualquier otra palabra corta).
    -   **Valor**: La URL completa a la que quieres redirigir (ej: `https://www.google.com`).
    -   **TTL**: El más bajo posible (ej: 1 minuto).

4.  **Levantar el entorno de desarrollo:**
    vagrant up
    Este comando creará una máquina virtual, instalará Python y todas las dependencias necesarias.

5.  **Ejecutar la API:**
    -   Conéctate a la máquina virtual:
        vagrant ssh
    -   Dentro de la máquina, navega al directorio del proyecto, activa el entorno virtual y lanza el servidor:
        cd /vagrant
        source venv/bin/activate
        uvicorn api.main:app --host 0.0.0.0 --port 8000

6.  **Probar el acortador:**
    -   Abre tu navegador web y visita `http://localhost:8000/test`.
    -   Si todo está configurado correctamente, deberías ser redirigido a `https://www.google.com`.