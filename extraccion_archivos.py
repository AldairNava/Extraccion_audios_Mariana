import os
import shutil
import patoolib
import patoolib.util
import sys

def limpiar_carpeta(carpeta):
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        try:
            if os.path.isfile(ruta) or os.path.islink(ruta):
                os.unlink(ruta)
            elif os.path.isdir(ruta):
                shutil.rmtree(ruta)
        except Exception as e:
            print(f'Error al eliminar {ruta}. Razón: {e}')

def mover_y_extraer(nombre_prefijo, carpeta_destino, contrasenas):
    carpeta_descargas = os.path.join(os.environ['USERPROFILE'], 'Downloads')
    # Buscar el primer ZIP que contenga el prefijo
    for archivo in os.listdir(carpeta_descargas):
        if nombre_prefijo in archivo and archivo.lower().endswith('.zip'):
            origen = os.path.join(carpeta_descargas, archivo)
            destino = os.path.join(carpeta_destino, archivo)

            print(f"Moviendo archivo {archivo} a {destino}...")
            shutil.move(origen, destino)

            # Intentar extracción con cada contraseña
            for pwd in contrasenas:
                try:
                    print(f"Extrayendo {archivo} en {carpeta_destino} con contraseña '{pwd}'…")
                    patoolib.extract_archive(destino,
                                             outdir=carpeta_destino,
                                             password=pwd)
                    break
                except patoolib.util.PatoolError as e:
                    print(f"  ⚠️ Error extrayendo con '{pwd}': {e}")
            else:
                print("  ❌ No se pudo extraer completamente con ninguna contraseña.")

            # 1) Eliminar carpetas vacías
            for entry in os.listdir(carpeta_destino):
                ruta_entry = os.path.join(carpeta_destino, entry)
                if os.path.isdir(ruta_entry):
                    # buscar mp3 dentro
                    mp3s = [f for f in os.listdir(ruta_entry)
                            if f.lower().endswith('.mp3')]
                    if not mp3s:
                        shutil.rmtree(ruta_entry)
                        print(f"Eliminada carpeta vacía: {entry}")

            # 2) Contar archivos .mp3 extraídos
            total_mp3 = 0
            for root, _, files in os.walk(carpeta_destino):
                total_mp3 += sum(1 for f in files
                                  if f.lower().endswith('.mp3'))
            print(f"✅ Se extrajeron {total_mp3} archivos .mp3 en '{carpeta_destino}'.")

            return

    print(f"No se encontró ningún ZIP con prefijo '{nombre_prefijo}' en Descargas.")

def main(i):
    carpetas = {
        '0': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_rar",
        '1': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_rar",
        '2': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\retenciones_rar",
        '3': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\servicios_apodaca_rar",
        '4': r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_rar\soporte_apodaca_rar"
    }
    contrasenas = ['Cyb*^1234567']

    carpeta_destino = carpetas.get(i)
    if not carpeta_destino:
        print(f"El valor '{i}' no es válido. Usa un número entre 0 y 4.")
        return
    
    if i in ('0', '1', '2'):
        nombre_prefijo = "p-efgarciac"
    else:
        nombre_prefijo = "cmanriquez"

    mover_y_extraer(nombre_prefijo, carpeta_destino, contrasenas)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Por favor, proporciona un índice (0–4) como argumento de línea de comandos.")
