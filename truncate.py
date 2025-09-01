import mysql.connector
from Tele import send_msg

def truncate_table(database, tabla):
    """Función para realizar TRUNCATE en una tabla específica de una base de datos."""
    conexion = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="thor",
        database=database
    )
    cursor = conexion.cursor()

    try:
        cursor.execute(f"TRUNCATE {database}.{tabla};")
        print(f"Tabla {tabla} truncada exitosamente en la base {database}.")
    except mysql.connector.Error as err:
        error_message = f"Error al truncar la tabla {tabla} en la base {database}: {err}"
        print(error_message)
        send_msg(error_message)
    finally:
        cursor.close()
        conexion.close()

def main():
    tablas_mariana = [
        "reporte_audios_servicios",
        "reporte_audios_servicios_apodaca",
        "reporte_audios_soporte",
        "reporte_audios_soporte_apodaca",
        "reporte_audios_retenciones",
        "reporteAudiosServiciosSpeech",
        "reporteAudiosSoporteSpeech",
        "reporteAudiosRetencionesSpeech",
        "reporteAudiosServiciosApodacaSpeech",
        "reporteAudiosSoporteApodacaSpeech",
        "reporteAudiosteleventasSpeech"
    ]
    
    tablas_avena = [
        "reporte_audios_retenciones"
    ]
    for tabla in tablas_mariana:
        truncate_table("audios_dana", tabla)
    for tabla in tablas_avena:
        truncate_table("marianaavena", tabla)

if __name__ == "__main__":
    main()
