import pandas as pd

def remove_mp3_from_excel(file_path, output_path):
    # Leer el archivo de Excel
    df = pd.read_excel(file_path)

    # Asegurarse de que solo hay una columna
    if df.shape[1] != 1:
        raise ValueError("El archivo de Excel debe tener una sola columna.")

    # Eliminar la extensión .mp3 de cada registro
    df.iloc[:, 0] = df.iloc[:, 0].str.replace('.mp3', '', regex=False)

    # Guardar el resultado en un nuevo archivo de Excel
    df.to_excel(output_path, index=False)
    print(f"Archivo procesado y guardado en: {output_path}")

if __name__ == "__main__":
    # Ruta del archivo de entrada y salida
    input_file = r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\Book1.xlsx'
    output_file = r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\Book2.xlsx'

    remove_mp3_from_excel(input_file, output_file)
