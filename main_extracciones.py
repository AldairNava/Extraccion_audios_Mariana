import os
import subprocess
import threading
import time
from datetime import datetime
from Tele import send_msg
import requests

def lanzar_script(script):
    """Lanza un script Python y espera a que termine."""
    subprocess.run(["python", script], check=True)

def ejecutar_tareas_con_valor():
    # 1) Tareas iniciales en serie
    iniciales = [
        ("Limpiando carpetas de audios", "eliminar_audios.py", 1),
        ("Limpiando carpetas raw",       "eliminar_rar.py",   1),
        ("Limpiando tablas",             "truncate.py",       1),
    ]
    for descripcion, script, delay in iniciales:
        print(f"\n{descripcion}")
        send_msg(f"\n{descripcion}")
        lanzar_script(script)
        time.sleep(delay)

    # 2) Extracciones paralelas
    extracciones = [
        ("Iniciando Extracción CDMX",     "extraccion_speech_cdmx_cue.py"),
        # ("Iniciando Extracción Apodaca",  "extraccion_speech_apo.py"),
    ]
    threads = []
    for descripcion, script in extracciones:
        print(f"\n{descripcion}")
        send_msg(f"\n{descripcion}")
        t = threading.Thread(target=lanzar_script, args=(script,))
        t.start()
        threads.append(t)

    # Esperamos a que ambas extracciones terminen
    for t in threads:
        t.join()

    # 3) Resto de tareas en serie
    restantes = [
        ("Evitando posible duplicidad",           "evitar_duplicidad.py",             5),
        ("Insertando registros para Avena",       "insertar_reporte_avena.py",        5),
        ("Ejecutando procedimientos Mariana",     "Procesos_MySQL.py",                5),
        ("Ejecutando procedimientos Avena",       "ProcesoMSQL_avena.py",             5),
        ("Subiendo audios avena",                 "mover_audios_filtrados_avena.py",  1),
        ("Subiendo audios mariana",               "mover_audios_filtrados.py",        1),
        ("Actualizando not found",                "buscar_ftp.py",                    1),
    ]
    for descripcion, script, delay in restantes:
        print(f"\n{descripcion}")
        send_msg(f"\n{descripcion}")
        lanzar_script(script)
        time.sleep(delay)

    # 4) Transcripción y validación final
    print("\nIniciando transcripción")
    send_msg("\nIniciando transcripción")
    iniciar_proceso_transcripcion()

    print("\nValidando asignaciones")
    send_msg("\nValidando asignaciones")
    lanzar_script("validacion_asignaciones.py")

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
    # Asignaciones solo los martes (weekday()==1)
    if datetime.now().weekday() == 1:
        print("Hoy es martes: ejecutando asignaciones...")
        lanzar_script("update_asignaciones.py")
        lanzar_script("Update_asignaciones_avena.py")
    else:
        print("No es martes: se omiten las asignaciones.")

    ejecutar_tareas_con_valor()
