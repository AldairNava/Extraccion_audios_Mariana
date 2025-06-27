import os
import subprocess
import schedule
import time
from datetime import datetime, timedelta
from Tele import send_msg
import requests

def ejecutar_tareas_con_valor():

    # print(f"\nIniciando proceso de extracción de audios cdmx_cuer con valor")
    # send_msg("Iniciando la descarga de CDMX")
    # subprocess.run(["python", "extraccion_speech_cdmx_cue.py"], check=True)
    # time.sleep(5)

    print(f"\nIniciando proceso de extracción de audios apodaca con valor")
    send_msg("Iniciando la descarga de Apodaca")
    subprocess.run(["python", "extraccion_speech_apo.py"], check=True)
    time.sleep(5)

    send_msg("Quitando registros Previos")
    print("Quitando registros Previos")
    subprocess.run(["python", "evitar_duplicidad.py"], check=True)
    time.sleep(5)

    send_msg("Insertando registros a avena")
    print("Insertando registros a avena")
    subprocess.run(["python", "insertar_reporte_avena.py"], check=True)
    time.sleep(5)

    send_msg("Ejecutando los Procedimeintos de CDMX")
    print("Ejecutando los Procedimeintos de CDMX")
    subprocess.run(["python", "Procesos_MySQL.py"], check=True)
    time.sleep(5)

    send_msg("Iniciando los procesos de avena")
    print("Iniciando los procesos de avena")
    subprocess.run(["python", "ProcesoMSQL_avena.py"], check=True)
    time.sleep(5)

    send_msg("Subiendo Audios de avena")
    print("Subiendo Audios de avena")
    subprocess.run(["python", "mover_audios_filtrados_avena.py"], check=True)

    send_msg("Subiendo Audios de Mariana")
    print("Subiendo Audios de Mariana")
    subprocess.run(["python", "mover_audios_filtrados.py"], check=True)

    print("Actualizando Not Found")
    subprocess.run(["python", "buscar_ftp.py"], check=True)

    send_msg("Iniciando la transcripcion")
    print("Iniciando la transcripcion")
    iniciar_proceso_transcripcion()

    print("Validando Asignaciones")
    send_msg("Validando Asignaciones")
    subprocess.run(["python", "validacion_asignaciones.py"], check=True)

def main():
    print("Esperando Horario de Ejecución Extracción Mariana...")
    schedule.every().monday.at("12:00").do(lambda: subprocess.run(["python", "update_asignaciones.py"], check=True))
    schedule.every().monday.at("12:01").do(lambda: subprocess.run(["python", "Update_asignaciones_avena.py"], check=True))
    schedule.every().monday.at("12:02").do(lambda: subprocess.run(["python", "eliminar_audios.py"], check=True))
    schedule.every().monday.at("23:58").do(lambda: subprocess.run(["python", "eliminar_rar.py"], check=True))
    schedule.every().day.at("23:59").do(lambda: subprocess.run(["python", "truncate.py"], check=True))
    schedule.every().day.at("00:00").do(ejecutar_tareas_con_valor)

    while True:
        schedule.run_pending()
        time.sleep(1)

def iniciar_proceso_transcripcion():
    url = "http://192.168.51.167:5000/iniciarProcesoTranscripcion"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            print("Correcto")
        else:
            print(f"Error: Código de estado {response.status_code}")
            send_msg(f"Error al mandar a Transcribir {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")


        

if __name__ == "__main__":
    main()
    # ejecutar_tareas_con_valor()