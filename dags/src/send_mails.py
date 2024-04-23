from datetime import datetime
from email import message
import pandas as pd
import smtplib
import os
from dotenv import dotenv_values

path = os.environ['AIRFLOW_HOME']

try:
    # Leer las credenciales desde el archivo .env
    credentials = dotenv_values(f'{path}/dags/env/email_key.env')
    user = credentials.get('user')
    password = credentials.get('password')
    if not user or not password:
        raise ValueError("Error: No se encontraron credenciales en el archivo .env.")
except FileNotFoundError:
    print("Error: No se encontró el archivo .env en la ruta especificada.")
    exit(1)
except ValueError as e:
    print(e)
    exit(1)

# Definimos el umbral % máximo tolerable de bicicletas fuera de servicio
umbral = 20 # valor x default
try:
    credentials = dotenv_values(f'{path}/dags/params/umbral.env')
    umbral_str = credentials.get('umbral')
    if umbral_str:
        umbral = float(umbral_str)
        if not 0 <= umbral <= 100:
            raise ValueError("Error: El umbral debe ser un número entre 0 y 100.")
    else:
        print("Advertencia: No se encontró valor para el umbral. Se usará 20% por default.")
except ValueError as e:
    print(e)
    exit(1)
except FileNotFoundError:
    print("Error: No se encontró el archivo .env en la ruta especificada.")
    exit(1)

print(f"Umbral válido: {umbral}%")
    
# Leo los destinatarios para la lista de distribución del mail
destinatarios = []
try:
    with open(f'{path}/dags/params/destinatarios.txt', 'r') as file:
        for line in file:
            destinatario = line.strip()
            destinatarios.append(destinatario)
except Exception as e:
    print(f'Error al leer el archivo de destinatarios: {e}')
    destinatarios = ['no_email@yahoo.com']

def enviar_mail_diario(destinatarios, user, password, texto_mail, asunto):
    """
    Envía un correo electrónico a una lista de destinatarios.

    Args:
    destinatarios (list): Lista de direcciones de correo electrónico de los destinatarios.
    user (str): Usuario del correo electrónico remitente.
    password (str): Contraseña del correo electrónico remitente.
    texto_mail (str): Cuerpo del correo electrónico a enviar.
    asunto (str): Asunto del correo electrónico.

    Returns:
    None
    """
    try:
        x = smtplib.SMTP('smtp.gmail.com', 587)
        x.starttls()
        x.login(user, password)
        subject = asunto
        body_text = texto_mail
        for destinatario in destinatarios:
            message = f'Subject: {subject}\n\n{body_text}'
            x.sendmail(user, destinatario, message.encode('utf-8'))
        x.quit()
        print('Éxito: Correo enviado a todos los destinatarios.')
    except Exception as exception:
        print(exception)
        print('Error: No se pudo enviar el correo.')
        
# Leer el archivo csv de estaciones fuera de servicio
df_est_oos = pd.read_csv(f'{path}/dags/data/station_availability.csv')

# Me quedo con el último dato
fila_mayor_fecha = df_est_oos[df_est_oos['last_refresh'] == df_est_oos['last_refresh'].max()]

# Obtener los valores necesarios
fecha_str = fila_mayor_fecha['last_refresh'].iloc[0]
fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y")
porcentaje_end_of_life = fila_mayor_fecha['%_END_OF_LIFE'].iloc[0]
total_flota = fila_mayor_fecha['END_OF_LIFE'].iloc[0] + fila_mayor_fecha['IN_SERVICE'].iloc[0]
    
if porcentaje_end_of_life < umbral:
    asunto = 'Reporte diario Ecobici'
    texto_mail = f"El {fecha} tenemos {porcentaje_end_of_life:.2f}% de bicicletas fuera de servicio sobre una flota total de {total_flota}"
else:
    asunto = 'ALERTA | Servicio Ecobici Comprometido'
    texto_mail = f"El {fecha} tenemos {porcentaje_end_of_life:.2f}% de bicicletas fuera de servicio!!!! \n\n Se superó el umbral máximo de {umbral}%"

print(texto_mail)
print(f'Umbral = {umbral}')
print(destinatarios)
enviar_mail_diario(destinatarios, user, password, texto_mail, asunto)