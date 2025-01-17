import os
import subprocess
import schedule
import time
from datetime import datetime, timedelta
from Tele import send_msg

def ejecutar_tareas_con_valor(x):
    if x == 1:
        mensaje = f"Iniciando proceso de extracción de audios Horario de 7 a 1 pm"
        print(mensaje)
        send_msg(mensaje)
    elif x == 2:
        mensaje = f"Iniciando proceso de extracción de audios Horario de 1 a 6 pm"
        print(mensaje)
        send_msg(mensaje)
    elif x == 3:
        mensaje = f"Iniciando proceso de extracción de audios Horario de 6 a 9 pm"
        print(mensaje)
        send_msg(mensaje)

    print(f"\nIniciando proceso de extracción de audios cdmx_cuer con valor {x}")
    subprocess.run(["python", "extraccion_speech_cdmx_cue.py", str(x)], check=True, capture_output=True, text=True)
    time.sleep(5)

    print(f"\nIniciando proceso de extracción de audios apodaca con valor {x}")
    subprocess.run(["python", "extraccion_speech_apo.py", str(x)], check=True, capture_output=True, text=True)
    time.sleep(5)

def main():
    print("Esperando Horario de Ejecución Extracción Mariana...")
    schedule.every().monday.at("12:00").do(lambda: subprocess.run(["python", "update_asignaciones.py"], check=True))
    schedule.every().day.at("13:00").do(lambda: subprocess.run(["python", "truncate.py"], check=True))
    schedule.every().day.at("13:01").do(ejecutar_tareas_con_valor, x=1)
    schedule.every().day.at("18:00").do(ejecutar_tareas_con_valor, x=2)
    schedule.every().day.at("20:30").do(ejecutar_tareas_con_valor, x=3)
    schedule.every().day.at("00:00").do(lambda: subprocess.run(["python", "Procesos_MySQL.py"], check=True))
    # schedule.every().day.at("00:45").do(lambda: subprocess.run(["python", "mover_audios_filtrados.py"], check=True))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
