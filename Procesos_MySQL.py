import mysql.connector
import time
from Tele import send_msg
from datetime import datetime, timedelta

UMBRAL_DANA = 700
UMBRAL_SPEECH = 7000
PAUSA_SEGUNDOS = 2

def verificar_registros(consulta, cursor, procedimiento, tabla, conexion):
    """
    Solo ejecuta el procedimiento si hay al menos un registro en la tabla respectiva.
    """
    try:
        cursor.execute(consulta)
        hay_registros = cursor.fetchone() is not None
    except mysql.connector.Error as err:
        msg = f"Error verificando {tabla}: {err}"
        print(msg)
        send_msg(msg)
        return False

    if not hay_registros:
        print(f"No hay registros en la tabla de {tabla}, NO se ejecuta {procedimiento}")
        time.sleep(PAUSA_SEGUNDOS)
        return False

    print(f"Se encontraron registros en la tabla de: {tabla}. Ejecutando {procedimiento}...")
    try:
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        cursor.execute(f"CALL {procedimiento}()")
        conexion.commit()
        print(f"Procedimiento {procedimiento} ejecutado.")
        return True
    except mysql.connector.Error as err:
        error_message = f"Error al ejecutar {procedimiento}: {err}"
        print(error_message)
        send_msg(error_message)
        return False
    finally:
        time.sleep(PAUSA_SEGUNDOS)

def contar_registros(cursor, tabla, fecha, status='Pendiente'):
    sql_count = f"""
        SELECT COUNT(*)
        FROM {tabla}
        WHERE DATE(fecha_llamada) = %s AND status = %s
    """
    cursor.execute(sql_count, (fecha, status))
    row = cursor.fetchone()
    return row[0] if row else 0

def main():
    try:
        conexion_dana = mysql.connector.connect(
            host="192.168.51.210",
            user="root",
            password="thor",
            database="audios_dana"
        )
        cursor_dana = conexion_dana.cursor()
    except mysql.connector.Error as err:
        print(f"No se pudo conectar a audios_dana: {err}")
        send_msg(f"No se pudo conectar a audios_dana: {err}")
        return

    consultas_y_procedimientos_dana = [
        ("SELECT 1 FROM audios_dana.reporte_audios_retenciones LIMIT 1;", "Sp_AsignacioneRetencionCDMXCV_intervalos_Temporales", "retenciones"),
        ("SELECT 1 FROM audios_dana.reporte_audios_servicios LIMIT 1;", "Sp_AsignacioneServiciosCDMX_intervalos_temporales", "servicios"),
        ("SELECT 1 FROM audios_dana.reporte_audios_servicios_apodaca LIMIT 1;", "Sp_AsignacioneServiciosApodaca_intervalos_temporales", "servicios_apodaca"),
        ("SELECT 1 FROM audios_dana.reporte_audios_soporte LIMIT 1;", "Sp_AsignacioneSoporteCDMXCV_intervalos_temporales", "soporte"),
        ("SELECT 1 FROM audios_dana.reporte_audios_soporte_apodaca LIMIT 1;", "Sp_AsignacioneSoporteAPODACA_intervalos_temporales", "soporte_apodaca")
    ]

    # BLOQUE AUDIOS_DANA
    try:
        hoy = datetime.now().date()
        cantidad = contar_registros(cursor_dana, "audios_dana.audios", hoy)
        print(f"Registros en audios_dana para {hoy}: {cantidad}")

        if cantidad < UMBRAL_DANA:
            print(f"Menos de {UMBRAL_DANA} → ejecutando procedimientos de audios_dana una sola vez...")
            for consulta, procedimiento, tabla in consultas_y_procedimientos_dana:
                verificar_registros(consulta, cursor_dana, procedimiento, tabla, conexion_dana)

            cantidad_post = contar_registros(cursor_dana, "audios_dana.audios", hoy)
            print(f"Recuento tras ejecutar procedimientos: {cantidad_post}")
        else:
            print(f"Ya hay {cantidad} (≥ {UMBRAL_DANA}). No se ejecutan procedimientos de audios_dana.")

        # BLOQUE AUDIOS_SPEECH
        cantidad_speech = contar_registros(cursor_dana, "audios_dana.audiosSpeech", hoy)
        print(f"Registros en audiosSpeech para {hoy}: {cantidad_speech}")

        procedimientos_speech = [
            ("SELECT 1 FROM audios_dana.reporteAudiosSoporteSpeech LIMIT 1;",        "Sp_AsignacionSoporteCDMXSpeech",         "reporteAudiosSoporteSpeech"),
            ("SELECT 1 FROM audios_dana.reporteAudiosSoporteApodacaSpeech LIMIT 1;", "Sp_AsignacionSoporteApodacaSpeech",      "reporteAudiosSoporteApodacaSpeech"),
            ("SELECT 1 FROM audios_dana.reporteAudiosServiciosSpeech LIMIT 1;",      "Sp_AsignacionServiciosCDMXSpeech",       "reporteAudiosServiciosSpeech"),
            ("SELECT 1 FROM audios_dana.reporteAudiosServiciosApodacaSpeech LIMIT 1;","Sp_AsignacionServiciosApodacaSpeech",    "reporteAudiosServiciosApodacaSpeech"),
            ("SELECT 1 FROM audios_dana.reporteAudiosteleventasSpeech LIMIT 1;",     "Sp_AsignacionTeleventasSpeech",          "reporteAudiosteleventasSpeech"),
            ("SELECT 1 FROM audios_dana.reporteAudiosRetencionesSpeech LIMIT 1;",    "Sp_AsignacionRetencionSpeech",           "reporteAudiosRetencionesSpeech")
        ]

        if cantidad_speech < UMBRAL_SPEECH:
            print(f"Menos de {UMBRAL_SPEECH} → ejecutando procedimientos de audiosSpeech una sola vez...")
            for consulta, procedimiento, tabla in procedimientos_speech:
                verificar_registros(consulta, cursor_dana, procedimiento, tabla, conexion_dana)

            cantidad_speech_post = contar_registros(cursor_dana, "audios_dana.audiosSpeech", hoy)
            print(f"Recuento tras ejecutar procedimientos audiosSpeech: {cantidad_speech_post}")
        else:
            print(f"Ya hay {cantidad_speech} (≥ {UMBRAL_SPEECH}). No se ejecutan procedimientos de audiosSpeech.")

    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
        send_msg(f"Error de MySQL en el flujo principal: {err}")
    finally:
        try: cursor_dana.close()
        except Exception: pass
        try: conexion_dana.close()
        except Exception: pass

if __name__ == "__main__":
    main()
