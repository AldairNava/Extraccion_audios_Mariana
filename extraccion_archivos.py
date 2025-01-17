import os
import shutil
import patoolib
from time import sleep
import sys

def mover_archivo(nombre_archivo, carpeta_destino):
    carpeta_descargas = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    
    for archivo in os.listdir(carpeta_descargas):
        if nombre_archivo in archivo:
            ruta_archivo_origen = os.path.join(carpeta_descargas, archivo)
            ruta_archivo_destino = os.path.join(carpeta_destino, archivo)
            
            print(f"Moviendo archivo {archivo} a {ruta_archivo_destino}...")
            shutil.move(ruta_archivo_origen, ruta_archivo_destino)
            print(f"Archivo {archivo} movido a {ruta_archivo_destino}")
            
            if archivo.endswith('.zip'):
                try:
                    print(f"Extrayendo archivo {archivo} en {carpeta_destino}...")
                    patoolib.extract_archive(ruta_archivo_destino, outdir=carpeta_destino, password="Cyb*^1234567")
                    print(f"Archivo {archivo} extraído en {carpeta_destino}")
                    
                    # Contar el número de archivos extraídos
                    archivos_extraidos = os.listdir(carpeta_destino)
                    num_archivos_extraidos = len(archivos_extraidos)
                    print(f"Se extrajeron {num_archivos_extraidos} archivos del archivo ZIP.")
                except patoolib.util.PatoolError as e:
                    print(f"No se pudo extraer {archivo}: {e}")
            
            return
    
    print(f"No se encontró ningún archivo que contenga '{nombre_archivo}' en la carpeta {carpeta_descargas}")

def main(i):
    nombre_archivo = "p-efgarciac"
    carpetas_destino = {
        '0': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_rar",
        '1': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_rar",
        '2': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\retenciones_rar",
        '3': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_apodaca_rar",
        '4': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_apodaca_rar"
    }

    carpeta_destino = carpetas_destino.get(i)
    if carpeta_destino:
        mover_archivo(nombre_archivo, carpeta_destino)
    else:
        print(f"El valor '{i}' no es válido. Por favor, proporciona un valor entre 0 y 4.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        i = sys.argv[1]
        main(i)
    else:
        print("Por favor, proporciona el nombre del archivo como argumento de línea de comandos.")
        
    # i = "3"
    # main(i)