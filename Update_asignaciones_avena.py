import mysql.connector
from Tele import send_msg

def main():
    conexion = mysql.connector.connect(
        host="192.168.51.210",
        user="root",
        password="",
        database="marianaavena"
    )
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE tabla_historico_asignaciones
            SET Lunes = 0, Martes = 0, Miercoles = 0, Jueves = 0, Viernes = 0, Sabado = 0, Domingo = 0;
        """)
        print("Tabla 'tabla_historico_asignaciones' actualizada exitosamente.")
        conexion.commit()
    except mysql.connector.Error as err:
        error_message = f"Error al actualizar la tabla: {err}"
        print(error_message)
        send_msg(error_message)
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    main()
