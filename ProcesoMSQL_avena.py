import mysql.connector
import time
from Tele import send_msg

def verificar_registros(consulta, cursor, procedimiento, tabla, conexion):
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    if not resultados:
        mensaje = f"No hay registros en la tabla de {tabla}"
        print(mensaje)
        send_msg(mensaje)
        time.sleep(2)
    else:
        print(f"Se Encontraron Registro en la tabla de: {tabla}:")
        print("Quitando Modo Seguro")
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        try: 
            cursor.execute(f"CALL {procedimiento}()") 
            print(f"Procedimiento {procedimiento} ejecutado.") 
            conexion.commit()
        except mysql.connector.Error as err: 
            error_message = f"Error al ejecutar el procedimiento {procedimiento}: {err}" 
            print(error_message) 
            send_msg(error_message)
        time.sleep(2)

def main():
    conexion = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="thor",
        database="marianaavena"
    )
    cursor = conexion.cursor()

    consultas_y_procedimientos = [
        ("SELECT * FROM marianaavena.reporte_audios_retenciones;", "Sp_AsignacioneRetencionCDMXCV", "retenciones")
    ]

    try:
        for consulta, procedimiento, tabla in consultas_y_procedimientos:
            verificar_registros(consulta, cursor, procedimiento, tabla, conexion)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        send_msg(f"Error: {err}")

    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    main()
