### Instructivo para ejecutar el proceso ETL en Airflow con Docker

#### Paso 1: Preparación de archivos

1. Descarga todos los archivos originales necesarios para el proceso ETL (scripts Python y archivos `.env`).
2. Coloca los archivos descargados en una carpeta llamada `C:\ecobici` en tu sistema.

#### Paso 2: Creación del Dockerfile

1. Abre tu editor de texto preferido y copia el contenido del Dockerfile proporcionado en un nuevo archivo.
2. Guarda este archivo con el nombre `Dockerfile` en la carpeta `C:\ecobici`.

#### Paso 3: Construcción de la imagen Docker

1. Abre PowerShell en tu sistema.
2. Navega hasta la carpeta `C:\ecobici` usando el comando `C:\cd ecobici`.
3. Ejecuta el siguiente comando para construir la imagen Docker: `docker build -t ecobici_etl` .

#### Paso 4: Ejecución del contenedor Docker

1. Una vez que la imagen Docker se haya construido correctamente, ejecuta el siguiente comando para iniciar el contenedor: `docker run -d -p 8080:8080 -p 5555:5555 ecobici_etl`.


#### Paso 5: Acceso a Airflow

1. Abre un navegador web y navega a `http://localhost:8080`.
2. Inicia sesión en Airflow con las siguientes credenciales:
- **Usuario**: airflow
- **Contraseña**: airflow

#### Paso 6: Verificación del proceso ETL

1. Una vez iniciada la sesión en Airflow, verás el DAG `ecobici_etl` en la lista de DAG disponibles.
2. Activa el DAG haciendo clic en el botón de encendido.
3. Airflow comenzará automáticamente a ejecutar el DAG según la programación definida en el mismo.