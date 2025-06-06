import os
import shutil
import patoolib
from time import sleep
import sys
import subprocess

def limpiar_carpeta(carpeta):
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)
        try:
            if os.path.isfile(ruta_archivo) or os.path.islink(ruta_archivo):
                os.unlink(ruta_archivo)
            elif os.path.isdir(ruta_archivo):
                shutil.rmtree(ruta_archivo)
        except Exception as e:
            print(f'Error al eliminar {ruta_archivo}. Razón: {e}')

def mover_archivo(nombre_archivo, carpeta_destino, contrasenas):
    carpeta_descargas = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    
    for archivo in os.listdir(carpeta_descargas):
        if nombre_archivo in archivo:
            ruta_archivo_origen = os.path.join(carpeta_descargas, archivo)
            ruta_archivo_destino = os.path.join(carpeta_destino, archivo)
            
            print(f"Moviendo archivo {archivo} a {ruta_archivo_destino}...")
            shutil.move(ruta_archivo_origen, ruta_archivo_destino)
            print(f"Archivo {archivo} movido a {ruta_archivo_destino}")
            
            if archivo.endswith('.zip'):
                exito_extraccion = False
                for contrasena in contrasenas:
                    try:
                        print(f"Extrayendo archivo {archivo} en {carpeta_destino} con la contraseña '{contrasena}'...")
                        patoolib.extract_archive(ruta_archivo_destino, outdir=carpeta_destino, password=contrasena)
                        print(f"Archivo {archivo} extraído en {carpeta_destino}")
                        
                        archivos_extraidos = os.listdir(carpeta_destino)
                        num_archivos_extraidos = len(archivos_extraidos)
                        print(f"Se extrajeron {num_archivos_extraidos} archivos del archivo ZIP.")
                        exito_extraccion = True
                        break
                    except patoolib.util.PatoolError as e:
                        print(f"No se pudo extraer {archivo} con la contraseña '{contrasena}': {e}")
                
                # if not exito_extraccion:
                #     shutil.move(ruta_archivo_destino, ruta_archivo_origen)
                #     print(f"Archivo {archivo} movido de vuelta a {ruta_archivo_origen}")
                #     limpiar_carpeta(carpeta_destino)
                #     print(f"Carpeta {carpeta_destino} ha sido limpiada.")
            
            return
    
    print(f"No se encontró ningún archivo que contenga '{nombre_archivo}' en la carpeta {carpeta_descargas}")

def main(i, manual):
    nombre_archivo = "cmanriquez"
    carpetas_destino = {
        '0': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_rar",
        '1': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_rar",
        '2': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\retenciones_rar",
        '3': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_apodaca_rar",
        '4': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_apodaca_rar"
    }

    contrasenas_manual = {
        '0': 'Cyb*^1234567',
        '1': 'Cyb*^1234567',
        '2': 'Cyb*^1234567',
        '3': 'Cyb*^1234567',
        '4': 'Cyb*^1234567'
    }

    contrasena_predeterminada = 'Cyb*^1234567'

    carpeta_destino = carpetas_destino.get(i)
    
    if manual:
        contrasena = contrasenas_manual.get(i)
        if carpeta_destino and contrasena:
            mover_archivo(nombre_archivo, carpeta_destino, [contrasena])
        else:
            print(f"El valor '{i}' no es válido o falta la contraseña. Por favor, proporciona un valor entre 0 y 4.")
    else:
        if carpeta_destino:
            mover_archivo(nombre_archivo, carpeta_destino, [contrasena_predeterminada])
        else:
            print(f"El valor '{i}' no es válido. Por favor, proporciona un valor entre 0 y 4.")

if __name__ == "__main__":
    manual = False
    if manual:
        i = "4"
        main(i, manual)
    else:
        if len(sys.argv) > 1:
            i = sys.argv[1]
            main(i, manual)
        else:
            print("Por favor, proporciona el nombre del archivo como argumento de línea de comandos.")
