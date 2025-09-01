import subprocess
import threading
import time
from datetime import datetime
from Tele import send_msg

def lanzar_script(script):
    """Lanza un script Python y espera a que termine."""
    subprocess.run(["python", script], check=True)

def ejecutar_tareas_con_valor():
    send_msg(f"Iniciando Extraccion de Audios")
    iniciales = [
        ("Limpiando carpetas de audios", "eliminar_audios.py", 1),
        ("Limpiando carpetas raw",       "eliminar_rar.py",   1),
        ("Limpiando tablas",             "truncate.py",       1),
    ]
    for descripcion, script, delay in iniciales:
        print(f"\n{descripcion}")
        # send_msg(f"\n{descripcion}")
        lanzar_script(script)
        time.sleep(delay)

    extracciones = [
        ("Iniciando Extracción CDMX",     "extraccion_speech_cdmx_cue.py"),
        ("Iniciando Extracción Apodaca",  "extraccion_speech_apo.py"),
    ]
    threads = []
    for descripcion, script in extracciones:
        print(f"\n{descripcion}")
        send_msg(f"\n{descripcion}")
        t = threading.Thread(target=lanzar_script, args=(script,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    # Asignaciones solo los martes (weekday()==1)
    if datetime.now().weekday() == 1:
        print("Hoy es martes: ejecutando asignaciones...")
        lanzar_script("update_asignaciones.py")
        # subprocess.run(["python", "limpiar_Ftp.py"])
    else:
        print("No es martes: se omiten las asignaciones.")

    ejecutar_tareas_con_valor()
