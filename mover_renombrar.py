import os
import shutil
import sys

def move_mp3_files(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    moved_files_count = 0  # Inicializar el contador

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".mp3"):
                original_file_path = os.path.join(root, file)

                base_name, extension = os.path.splitext(file)

                shortened_name = base_name[:32]

                new_file_name = shortened_name + extension

                dest_file_path = os.path.join(dest_dir, new_file_name)
                
                shutil.move(original_file_path, dest_file_path)
                moved_files_count += 1  # Incrementar el contador

    print(f"Se movieron {moved_files_count} archivos .mp3.")  # Imprimir el número de archivos movidos

def main(i):
    
    options = {
        "0": (r"C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_rar", r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_servicios"),
        "1": (r"C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_rar", r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_soporte"),
        "2": (r"C:\Extraccion_Mariana_Continuo\archivos_rar\retenciones_rar", r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_retenciones"),
        "3": (r"C:\Extraccion_Mariana_Continuo\archivos_rar\televentas_rar", r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_televentas"),
        "4": (r"C:\Extraccion_Mariana_Continuo\archivos_rar\servicios_apodaca_rar", r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_servicios_apo"),
        "5": (r"C:\Extraccion_Mariana_Continuo\archivos_rar\soporte_apodaca_rar", r"C:\Extraccion_Mariana_Continuo\carpeta_de_audios\audios_rar_soporte_apo")
    }
    
    if i in options:
        source_dir, dest_dir = options[i]
        move_mp3_files(source_dir, dest_dir)
    else:
        print("Valor de i no reconocido.")

if __name__ == "__main__":
    manual=False
    if manual ==True:
        i = "4"
        main(i)
    else:
        if len(sys.argv) > 1:
            i = sys.argv[1]
            main(f"{i}")
        else:
            print("Por favor, proporciona el nombre del archivo como argumento de línea de comandos.")
    