import mysql.connector
from Tele import send_msg

def main():
    conexion = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="",
        database="audios_dana"
    )
    cursor = conexion.cursor()

    tablas = [
        "reporte_audios_servicios",
        "reporte_audios_servicios_apodaca",
        "reporte_audios_soporte",
        "reporte_audios_soporte_apodaca",
        "reporte_audios_retenciones"
    ]

    try:
        for tabla in tablas:
            cursor.execute(f"TRUNCATE audios_dana.{tabla};")
            print(f"Tabla {tabla} truncada exitosamente.")
        conexion.commit()
    except mysql.connector.Error as err:
        error_message = f"Error al truncar la tabla: {err}"
        print(error_message)
        send_msg(error_message)
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    main()
