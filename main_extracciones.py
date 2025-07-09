import os
import subprocess
import schedule
import time
from datetime import datetime, timedelta
from Tele import send_msg
import requests

def ejecutar_tareas_con_valor():

    msg =f"\nLimpiando carpetas"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "eliminar_rar.py"], check=True)

    msg =f"\nLimpiando tablas"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "truncate.py"], check=True)

    msg =f"\nIniciando Extracción CDMX"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "extraccion_speech_cdmx_cue.py"], check=True)
    time.sleep(5)

    msg =f"\nIniciando Extracción de audios apodaca"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "extraccion_speech_apo.py"], check=True)
    time.sleep(5)

    msg =f"\nEvitando posible duplicidad"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "evitar_duplicidad.py"], check=True)
    time.sleep(5)

    msg =f"\nInsertando registros para Avena"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "insertar_reporte_avena.py"], check=True)
    time.sleep(5)

    msg =f"\nEjecutando procedimientos almacensado Mariana"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "Procesos_MySQL.py"], check=True)
    time.sleep(5)

    msg =f"\nEjecutando procedimientos almacenados Avena"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "ProcesoMSQL_avena.py"], check=True)
    time.sleep(5)

    msg =f"\nSubiendo audios avena"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "mover_audios_filtrados_avena.py"], check=True)

    msg =f"\nSubiendo audias mariana"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "mover_audios_filtrados.py"], check=True)

    msg =f"\nactualizando not found"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "buscar_ftp.py"], check=True)

    msg =f"\niniciando transcripcion"
    print(msg)
    send_msg(msg)
    iniciar_proceso_transcripcion()

    msg =f"\nvalidando asignaciones"
    print(msg)
    send_msg(msg)
    subprocess.run(["python", "validacion_asignaciones.py"], check=True)

def main():
    print("Esperando Horario de Ejecución Extracción Mariana...")
    schedule.every().monday.at("12:00").do(lambda: subprocess.run(["python", "update_asignaciones.py"], check=True))
    schedule.every().monday.at("12:01").do(lambda: subprocess.run(["python", "Update_asignaciones_avena.py"], check=True))
    schedule.every().monday.at("12:02").do(lambda: subprocess.run(["python", "eliminar_audios.py"], check=True))
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
    # main()
    ejecutar_tareas_con_valor()