import mysql.connector
import time
from Tele import send_msg
from datetime import datetime

PAUSA_SEGUNDOS = 2

# ==== BLOQUE AUDIOS (como antes) ====
PROCEDIMIENTOS_AUDIOS = [
    {
        "reporte": "reporte_audios_retenciones",
        "procedimiento": "Sp_AsignacioneRetencionCDMXCV_intervalos_Temporales",
        "tipo": "retenciones",
        "umbral": 100
    },
    {
        "reporte": "reporte_audios_servicios",
        "procedimiento": "Sp_AsignacioneServiciosCDMX_intervalos_temporales",
        "tipo": "servicios",
        "umbral": 300
    },
    {
        "reporte": "reporte_audios_servicios_apodaca",
        "procedimiento": "Sp_AsignacioneServiciosApodaca_intervalos_temporales",
        "tipo": "servicios",
        "umbral": 300
    },
    {
        "reporte": "reporte_audios_soporte",
        "procedimiento": "Sp_AsignacioneSoporteCDMXCV_intervalos_temporales",
        "tipo": "soporte",
        "umbral": 300
    },
    {
        "reporte": "reporte_audios_soporte_apodaca",
        "procedimiento": "Sp_AsignacioneSoporteAPODACA_intervalos_temporales",
        "tipo": "soporte",
        "umbral": 300
    }
]

# ==== BLOQUE SPEECH ====
PROCEDIMIENTOS_SPEECH = [
    {
        "reporte": "reporteAudiosSoporteSpeech",
        "procedimiento": "Sp_AsignacionSoporteCDMXSpeech",
        "tipo": "soporte",
        "umbral": 2450
    },
    {
        "reporte": "reporteAudiosSoporteApodacaSpeech",
        "procedimiento": "Sp_AsignacionSoporteApodacaSpeech",
        "tipo": "soporte",
        "umbral": 2450
    },
    {
        "reporte": "reporteAudiosServiciosSpeech",
        "procedimiento": "Sp_AsignacionServiciosCDMXSpeech",
        "tipo": "servicios",
        "umbral": 1750
    },
    {
        "reporte": "reporteAudiosServiciosApodacaSpeech",
        "procedimiento": "Sp_AsignacionServiciosApodacaSpeech",
        "tipo": "servicios",
        "umbral": 1750
    },
    {
        "reporte": "reporteAudiosteleventasSpeech",
        "procedimiento": "Sp_AsignacionTeleventasSpeech",
        "tipo": "ventas",
        "umbral": 1400
    },
    {
        "reporte": "reporteAudiosRetencionesSpeech",
        "procedimiento": "Sp_AsignacionRetencionSpeech",
        "tipo": "retenciones",
        "umbral": 1400
    }
]

def hay_registros_en_reporte(cursor, reporte):
    consulta = f"SELECT 1 FROM audios_dana.{reporte} LIMIT 1;"
    cursor.execute(consulta)
    return cursor.fetchone() is not None

def contar_registros(cursor, tabla, fecha, tipo):
    consulta = f"""
        SELECT COUNT(*) FROM audios_dana.{tabla}
        WHERE DATE(fecha_llamada) = %s AND tipo = %s
    """
    cursor.execute(consulta, (fecha, tipo))
    row = cursor.fetchone()
    return row[0] if row else 0

def ejecutar_procedimiento(cursor, conexion, procedimiento, reporte, umbral, total_actual):
    print(f"Total actual para {reporte}: {total_actual}. Umbral: {umbral}")
    if total_actual <= umbral:
        try:
            cursor.execute("SET SQL_SAFE_UPDATES = 0;")
            cursor.execute(f"CALL {procedimiento}()")
            conexion.commit()
            print(f"Procedimiento {procedimiento} ejecutado correctamente.")
            return True
        except mysql.connector.Error as err:
            msg = f"Error al ejecutar {procedimiento}: {err}"
            print(msg)
            send_msg(msg)
    else:
        print(f"Ya hay más de {umbral} registros para el tipo en la tabla. NO se ejecuta {procedimiento}")
    return False

def main():
    try:
        conexion = mysql.connector.connect(
            host="192.168.51.210",
            user="root",
            password="thor",
            database="audios_dana"
        )
        cursor = conexion.cursor()
    except mysql.connector.Error as err:
        print(f"No se pudo conectar a audios_dana: {err}")
        send_msg(f"No se pudo conectar a audios_dana: {err}")
        return

    hoy = datetime.now().date()

    # BLOQUE AUDIOS
    for proc in PROCEDIMIENTOS_AUDIOS:
        print(f"\n---- Procesando {proc['reporte']} (audios, tipo={proc['tipo']}, umbral={proc['umbral']}) ----")
        if hay_registros_en_reporte(cursor, proc["reporte"]):
            total_actual = contar_registros(cursor, "audios", hoy, proc["tipo"])
            ejecutar_procedimiento(cursor, conexion, proc["procedimiento"], proc["reporte"], proc["umbral"], total_actual)
        else:
            print(f"No hay registros en {proc['reporte']}, NO se ejecuta {proc['procedimiento']}")
        time.sleep(PAUSA_SEGUNDOS)

    # BLOQUE SPEECH
    for proc in PROCEDIMIENTOS_SPEECH:
        print(f"\n---- Procesando {proc['reporte']} (speech, tipo={proc['tipo']}, umbral={proc['umbral']}) ----")
        if hay_registros_en_reporte(cursor, proc["reporte"]):
            total_actual = contar_registros(cursor, "audiosSpeech", hoy, proc["tipo"])
            ejecutar_procedimiento(cursor, conexion, proc["procedimiento"], proc["reporte"], proc["umbral"], total_actual)
        else:
            print(f"No hay registros en {proc['reporte']}, NO se ejecuta {proc['procedimiento']}")
        time.sleep(PAUSA_SEGUNDOS)

    try:
        cursor.close()
        conexion.close()
    except Exception:
        pass

if __name__ == "__main__":
    main()
