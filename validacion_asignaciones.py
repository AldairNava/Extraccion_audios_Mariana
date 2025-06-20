import mysql.connector
from datetime import date, timedelta
from Tele import send_msg

def actualizar_historico():
    try:
        # 1) Conexión a la base de datos
        conexion = mysql.connector.connect(
            host="192.168.51.210",
            user="root",
            password="",
            database="audios_dana"
        )
        cursor = conexion.cursor()

        # 2) Determinar fecha de ayer y columna correspondiente
        ayer = date.today() - timedelta(days=1)
        # date.weekday(): 0=Lunes … 6=Domingo
        dias = {
            0: 'Lunes',
            1: 'Martes',
            2: 'Miercoles',
            3: 'Jueves',
            4: 'Viernes',
            5: 'Sabado',
            6: 'Domingo'
        }
        col_dia = dias[ayer.weekday()]

        # 3) Obtener agentes únicos con status de error de audio en la fecha de ayer
        cursor.execute(
            """
            SELECT DISTINCT agente
            FROM audios
            WHERE DATE(fecha_llamada) = %s
              AND status IN (%s, %s)
            """,
            (ayer, 'not found audio', 'error audio')
        )
        agentes = cursor.fetchall()

        # 4) Para cada agente, revisamos su valor actual y actualizamos según completados
        for (agente,) in agentes:
            # 4.1) Valor actual en historico
            cursor.execute(
                f"SELECT {col_dia} FROM tabla_historico_asignaciones WHERE No_Empleado = %s",
                (agente,)
            )
            fila = cursor.fetchone()
            if not fila:
                continue
            valor_actual = fila[0] or 0

            # 4.2) Si tenía más de 1 asignación, contamos los completados
            if valor_actual > 1:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM audios
                    WHERE DATE(fecha_llamada) = %s
                      AND agente = %s
                      AND status NOT IN (%s, %s)
                    """,
                    (ayer, agente, 'not found audio', 'error audio')
                )
                completados = cursor.fetchone()[0]
                nuevo_valor = completados
            else:
                # Si tenía 1 o menos, reseteamos a 0
                nuevo_valor = 0

            # 4.3) Ejecutar el UPDATE
            cursor.execute(
                f"""
                UPDATE tabla_historico_asignaciones
                SET {col_dia} = %s
                WHERE No_Empleado = %s
                """,
                (nuevo_valor, agente)
            )

        # 5) Confirmar cambios
        conexion.commit()
        print(f"Histórico actualizado para {ayer} en columna '{col_dia}'.")

    except mysql.connector.Error as err:
        msg = f"Error durante la actualización: {err}"
        print(msg)
        send_msg(msg)

    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    actualizar_historico()
