import mysql.connector
import time
from Tele import send_msg
from datetime import datetime, timedelta
import subprocess

def verificar_registros(consulta, cursor, procedimiento, tabla, conexion):
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    if not resultados:
        print(f"No hay registros en la tabla de {tabla}")
        time.sleep(2)
    else:
        print(f"Se encontraron registros en la tabla de: {tabla}")
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        try:
            cursor.execute(f"CALL {procedimiento}()")
            conexion.commit()
            print(f"Procedimiento {procedimiento} ejecutado.")
        except mysql.connector.Error as err:
            error_message = f"Error al ejecutar {procedimiento}: {err}"
            print(error_message)
            send_msg(error_message)
        time.sleep(2)

def main():
    conexion_dana = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="",
        database="audios_dana"
    )
    cursor_dana = conexion_dana.cursor()

    conexion_avena = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="",
        database="marianaavena"
    )
    cursor_avena = conexion_avena.cursor()

    consultas_y_procedimientos_dana = [
        ("SELECT * FROM audios_dana.reporte_audios_servicios;", 
         "Sp_AsignacioneServiciosCDMX_intervalos_temporales", "servicios"),
        ("SELECT * FROM audios_dana.reporte_audios_servicios_apodaca;", 
         "Sp_AsignacioneServiciosApodaca_intervalos_temporales", "servicios_apodaca"),
        ("SELECT * FROM audios_dana.reporte_audios_soporte;", 
         "Sp_AsignacioneSoporteCDMXCV_intervalos_temporales", "soporte"),
        ("SELECT * FROM audios_dana.reporte_audios_soporte_apodaca;", 
         "Sp_AsignacioneSoporteAPODACA_intervalos_temporales", "soporte_apodaca"),
        ("SELECT * FROM audios_dana.reporte_audios_retenciones;", 
         "Sp_AsignacioneRetencionCDMXCV_intervalos_Temporales", "retenciones")
    ]

    consultas_y_procedimientos_avena = [
        ("SELECT * FROM marianaavena.reporte_audios_retenciones;", 
         "Sp_AsignacioneRetencionCDMXCV", "retenciones")
    ]

    try:
        fecha_ayer = (datetime.now() - timedelta(days=1)).date()
        sql_count = """
            SELECT COUNT(*)
            FROM audios_dana.audios
            WHERE DATE(fecha_llamada) = %s
        """

        while True:
            for consulta, procedimiento, tabla in consultas_y_procedimientos_dana:
                verificar_registros(consulta, cursor_dana, procedimiento, tabla, conexion_dana)

            cursor_dana.execute(sql_count, (fecha_ayer,))
            cantidad = cursor_dana.fetchone()[0]
            print(f"Registros en audios_dana para {fecha_ayer}: {cantidad}")

            if cantidad >= 700:
                print("Se alcanzaron al menos 700 registros. Continuando con marianaavena…")
                break
            else:
                print("Menos de 700 registros, volviendo a ejecutar procedimientos en audios_dana.")
                time.sleep(5)

        for consulta, procedimiento, tabla in consultas_y_procedimientos_avena:
            verificar_registros(consulta, cursor_avena, procedimiento, tabla, conexion_avena)

    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
        send_msg(f"Error de MySQL en el flujo principal: {err}")

    finally:
        cursor_dana.close()
        conexion_dana.close()
        cursor_avena.close()
        conexion_avena.close()


if __name__ == "__main__":
    main()
