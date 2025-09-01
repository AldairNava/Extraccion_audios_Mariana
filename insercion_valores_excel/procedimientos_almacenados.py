import mysql.connector
from mysql.connector import Error
import time

def execute_stored_procedures():
    try:

        connection = mysql.connector.connect(
            host='192.168.51.210',
            database='audios_dana',
            user='root',
            password='thor'
        )

        if connection.is_connected():
            print("Conexión exitosa a la base de datos")

            cursor = connection.cursor()

            stored_procedures = [
                'CALL Sp_AsignacioneServiciosCDMXCV;',
                'CALL Sp_AsignacioneServiciosAPODACA;',
                'CALL Sp_AsignacioneSoporteCDMXCV;',
                'CALL Sp_AsignacioneSoporteAPODACA;',
                'CALL Sp_AsignacioneRetencionCDMXCV;'
            ]

            for procedure in stored_procedures:
                cursor.execute(procedure)
                connection.commit()
                print(f"Ejecutado: {procedure}")
                time.sleep(5)

            cursor.close()
            connection.close()
            print("Conexión cerrada")

    except Error as e:
        print(f"Error: {e}")
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada debido a un error")
            
execute_stored_procedures()
