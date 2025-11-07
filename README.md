############################################################################
#                                                                          #
#                      ACORTADOR DE URLS BASADO EN DNS                     #
#                                                                          #
#          Un servicio minimalista y potente que usa el Sistema de         #
#              Nombres de Dominio como su base de datos.                   #
#                                                                          #
############################################################################


============================================================================
## 1. INTRODUCCIÓN Y CONCEPTO
============================================================================

Bienvenido a este proyecto de acortador de URLs. A diferencia de los servicios tradicionales que dependen de bases de datos como MySQL o MongoDB para almacenar las correspondencias entre enlaces cortos y largos, este proyecto adopta un enfoque innovador y elegante: utiliza el propio Sistema de Nombres de Dominio (DNS) como una base de datos de tipo clave-valor.

El servicio está construido sobre un stack tecnológico moderno y eficiente:
- Backend: FastAPI, un framework de Python de alto rendimiento.
- Entorno de Desarrollo: Vagrant y VirtualBox, para crear un entorno de servidor aislado, consistente y reproducible con un solo comando.
- Lógica de Redirección: La librería dnspython para realizar las consultas DNS en tiempo real.

El resultado es un sistema ligero, escalable y fascinantemente simple.


============================================================================
## 2. ¿CÓMO FUNCIONA EXACTAMENTE?
============================================================================

La magia de este sistema reside en el uso de los registros DNS de tipo TXT. Un registro TXT permite asociar un texto arbitrario a un nombre de dominio. Nosotros aprovechamos esta característica para almacenar la URL de destino.

El flujo completo es el siguiente:

1. CREACIÓN DE UN ENLACE CORTO:
   - El administrador del servicio accede al panel de control de su proveedor de DNS (como IONOS).
   - Para crear el enlace corto "/yt", crea un nuevo registro TXT para el subdominio "yt.su-dominio.com".
   - En el campo "Valor" de este registro, introduce la URL completa de destino, por ejemplo, "https://www.youtube.com".

2. PETICIÓN DEL USUARIO FINAL:
   - Un usuario abre en su navegador la URL: http://localhost:8000/yt

3. PROCESAMIENTO EN EL BACKEND (FastAPI):
   - La aplicación FastAPI recibe la petición y extrae la ruta corta ("yt").
   - Concatena la ruta corta con el dominio base (configurado en el archivo .env) para construir el nombre de dominio completo a consultar: "yt.su-dominio.com".
   - Utiliza la librería `dnspython` para lanzar una consulta DNS al mundo, preguntando específicamente por el registro TXT asociado a "yt.su-dominio.com".

4. RESPUESTA Y REDIRECCIÓN:
   - Si los servidores DNS responden con el registro TXT, la aplicación extrae la URL de destino ("https://www.youtube.com") de su valor.
   - Inmediatamente, la API envía al navegador del usuario una respuesta de redirección HTTP (código 307 - Redirección Temporal), indicándole que la página que busca se encuentra en "https://www.youtube.com".
   - Si el subdominio no existe o no tiene un registro TXT, la API devuelve un error 404 (No Encontrado).


============================================================================
## 3. ESTRUCTURA DEL PROYECTO
============================================================================

El repositorio está organizado de la siguiente manera para mantener la claridad y la separación de responsabilidades:

.
├── api/
│   └── main.py       # El corazón de la aplicación. Contiene toda la lógica de FastAPI.
├── .env              # Fichero de configuración local para variables de entorno. ¡NUNCA SUBIR A GIT!
├── .env.example      # Plantilla de ejemplo para el fichero .env.
├── .gitignore        # Define qué ficheros y carpetas debe ignorar Git (como .env o la carpeta venv).
├── bootstrap.sh      # Script de aprovisionamiento. Se ejecuta al crear la máquina virtual para instalar todo lo necesario.
├── README            # Este mismo archivo de documentación.
├── requirements.txt  # Lista de todas las dependencias de Python que necesita el proyecto.
└── Vagrantfile       # El "plano" de nuestra máquina virtual. Define el sistema operativo, la red y qué script de aprovisionamiento usar.


============================================================================
## 4. REQUISITOS PREVIOS
============================================================================

Antes de comenzar, asegúrate de tener el siguiente software instalado y funcionando en tu ordenador:

- Vagrant: Una herramienta para construir y gestionar entornos de desarrollo virtualizados.
  > Descarga: https://www.vagrantup.com/downloads

- VirtualBox: El "proveedor" de virtualización que usará Vagrant para crear la máquina virtual.
  > Descarga: https://www.virtualbox.org/wiki/Downloads

- Un nombre de dominio: Necesitarás acceso al panel de configuración DNS de un dominio que poseas para poder crear los registros TXT.


============================================================================
## 5. GUÍA DE INSTALACIÓN Y PUESTA EN MARCHA PASO A PASO
============================================================================

Sigue estas instrucciones detalladas para levantar el servicio.

### PASO 1: OBTENER EL CÓDIGO FUENTE

Clona este repositorio en tu máquina local usando Git.

$ git clone <URL-del-repositorio>
$ cd <nombre-del-proyecto>

### PASO 2: CONFIGURAR TU DOMINIO BASE

El servicio necesita saber cuál es tu dominio para poder construir las consultas DNS. Esta configuración se gestiona a través de un archivo de entorno para no exponerla en el código.

# 1. Crea tu archivo de configuración personal a partir del ejemplo.
$ cp .env.example .env

# 2. Abre el nuevo archivo .env con un editor de texto y modifica la variable.
#    Reemplaza "tu-dominio.com" por tu dominio real.
BASE_DOMAIN=davidexposito.es

### PASO 3: CREAR TU PRIMER ENLACE CORTO EN EL DNS

Ahora, vamos a la parte más interesante: crear el "registro en la base de datos". Accede al panel de administración de tu dominio (ej. IONOS).

- Ve a la sección de gestión de DNS y elige "Añadir registro".
- Rellena los campos de la siguiente manera:
    - Tipo: TXT
    - Nombre de host: go  (Esta será la palabra que uses en la URL, ej. /go)
    - Valor: https://www.github.com (La URL completa a la que quieres redirigir)
    - TTL (Time To Live): 1 minuto (Usa el valor más bajo posible. Esto hará que futuros cambios en tus enlaces se propaguen más rápido por internet).
- Guarda el registro. Ten en cuenta que los cambios de DNS pueden tardar unos minutos en ser visibles globalmente.

### PASO 4: CONSTRUIR Y PROVISIONAR EL ENTORNO DE DESARROLLO

Este paso es casi mágico. Vagrant leerá el `Vagrantfile` y construirá una máquina virtual Ubuntu completa, ejecutará `bootstrap.sh` para instalar Python, pip, crear un entorno virtual e instalar todas las dependencias de `requirements.txt`.

# Desde la terminal de tu ordenador, en la carpeta del proyecto, ejecuta:
$ vagrant up

Verás mucho texto en la pantalla mientras Vagrant trabaja. Ten paciencia, la primera vez puede tardar varios minutos.

### PASO 5: EJECUTAR LA APLICACIÓN

Una vez que `vagrant up` termine, nuestro servidor está listo. Ahora solo necesitamos acceder a él y encender la API.

# 1. Conéctate a la máquina virtual recién creada mediante SSH.
$ vagrant ssh

# 2. Una vez dentro de la máquina virtual, navega al directorio del proyecto.
#    Este directorio está sincronizado con la carpeta de tu ordenador.
$ cd /vagrant

# 3. Activa el entorno virtual de Python donde están instaladas nuestras librerías.
$ source venv/bin/activate
#    (Verás que tu prompt de la terminal cambia para indicar que el entorno está activo).

# 4. Lanza el servidor web Uvicorn que ejecutará nuestra aplicación FastAPI.
$ uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

- --host 0.0.0.0: Hace que el servidor sea accesible desde fuera de la máquina virtual (es decir, desde el navegador de tu ordenador).
- --port 8000: Especifica el puerto en el que escuchará el servidor.
- --reload: Un modo de desarrollo muy útil que reinicia el servidor automáticamente cada vez que guardas un cambio en el código Python.

============================================================================
## 6. ¡A PROBAR!
============================================================================

Si todo ha ido bien, el servidor está ahora mismo corriendo y esperando peticiones.

Abre tu navegador web preferido y visita la siguiente dirección:

http://localhost:8000/go

Si configuraste el registro DNS del PASO 3 correctamente, deberías ser redirigido instantáneamente a https://www.github.com.

¡Felicidades, tu acortador de URLs basado en DNS está funcionando!

============================================================================
## 7. GESTIÓN DEL ENTORNO VAGRANT
============================================================================

Para gestionar tu máquina virtual, usa los siguientes comandos desde la terminal de tu ordenador (en la carpeta del proyecto):

- Para apagar la máquina virtual de forma segura:
  $ vagrant halt

- Para reanudar una máquina apagada:
  $ vagrant up

- Para suspender el estado actual de la máquina (como hibernar):
  $ vagrant suspend

- Para eliminar COMPLETAMENTE la máquina virtual (¡cuidado, esta acción no se puede deshacer!):
  $ vagrant destroy -f
