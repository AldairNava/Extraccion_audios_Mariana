import os
import subprocess
import schedule
import time
from datetime import datetime
from Tele import send_msg
import requests

def ejecutar_tareas_con_valor():
    tareas = [
        ("Limpiando carpetas de audios",          "eliminar_audios.py",            1),
        ("Limpiando carpetas raw",                "eliminar_rar.py",               1),
        ("Limpiando tablas",                      "truncate.py",                   1),
        ("Iniciando Extracción CDMX",             "extraccion_speech_cdmx_cue.py", 5),
        # ("Iniciando Extracción de audios apodaca","extraccion_speech_apo.py",      5),
        ("Evitando posible duplicidad",           "evitar_duplicidad.py",          5),
        ("Insertando registros para Avena",       "insertar_reporte_avena.py",     5),
        ("Ejecutando procedimientos almacenado Mariana","Procesos_MySQL.py",      5),
        ("Ejecutando procedimientos almacenados Avena","ProcesoMSQL_avena.py",      5),
        ("Subiendo audios avena",                 "mover_audios_filtrados_avena.py", 1),
        ("Subiendo audios mariana",               "mover_audios_filtrados.py",     1),
        ("Actualizando not found",                "buscar_ftp.py",                 1),
    ]
    
    for descripcion, script, delay in tareas:
        msg = f"\n{descripcion}"
        print(msg)
        send_msg(msg)
        subprocess.run(["python", script], check=True)
        if delay:
            time.sleep(delay)

    print("\nIniciando transcripción")
    send_msg("\nIniciando transcripción")
    iniciar_proceso_transcripcion()

    print("\nValidando asignaciones")
    send_msg("\nValidando asignaciones")
    subprocess.run(["python", "validacion_asignaciones.py"], check=True)

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
    if datetime.now().weekday() == 1:
        print("Hoy es martes: ejecutando asignaciones...")
        subprocess.run(["python", "update_asignaciones.py"], check=True)
        subprocess.run(["python", "Update_asignaciones_avena.py"], check=True)
    else:
        print("No es martes: se omite las asiganciones.")

    ejecutar_tareas_con_valor()