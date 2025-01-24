from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
import datetime
import random
import pandas as pd
import sys
import subprocess
import pyautogui


from utileria.utileria_genesys import *
pyautogui.FAILSAFE = False

def descargas_automatica_no_seguro(driver):
    print("\nIniciando ajuste descargas automáticas")

    for _ in range(7):
        element = driver.switch_to.active_element
        element.send_keys(Keys.TAB)
        sleep(1)
    
    element.send_keys(Keys.ENTER)
    sleep(2)
    
    element.send_keys(Keys.DOWN)
    sleep(2)
    
    element.send_keys(Keys.ENTER)
    sleep(2)
    
    print("\nIniciando ajuste descargas no seguras")
    
    for _ in range(5):
        element = driver.switch_to.active_element
        element.send_keys(Keys.TAB)
        sleep(1)
    
    element.send_keys(Keys.ENTER)
    sleep(2)
    
    element.send_keys(Keys.DOWN)
    sleep(2)
    
    element.send_keys(Keys.ENTER)
    sleep(2)

    


def obtener_vqd(i):
    archivos_excel = {
        "Listado de VQDs Servicios_APODACA": r"C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_vqd\Listado de VQDs Servicios Apocada.xlsx",
        "Listado de VQDs Soporte": r'C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\archivos_vqd\Listado de VQDs Soporte Apodaca.xlsx'
    }

    archivo_excel = archivos_excel[list(archivos_excel.keys())[i]]

    datos = pd.read_excel(archivo_excel)

    VQDs = []
    for index, row in datos.iterrows():
        if 2 <= index + 1 <= 29:
            VQDs.append(row[3])

    if len(VQDs) > 5:
        VQDs = random.sample(VQDs, 5)

    print("\nValores de VQD:")
    for VQD in VQDs:
        print(VQD)

    conteo_total_vqd = len(VQDs)
    print("\nConteo total de valores en VQD:", conteo_total_vqd)

    return VQDs


def agregar_valores_vqd(driver, i):
    valores_input = driver.find_element(By.XPATH, metadatos_valores_input)
    driver.execute_script("arguments[0].scrollIntoView(true);", valores_input)
    VQDs = obtener_vqd(i)
    valores_input.click()
    valores_input.send_keys(VQDs[0])
    sleep(2)
    valores_input_but_mas = driver.find_element(By.XPATH, metadatos_valores_boton_mas)
    driver.execute_script("arguments[0].scrollIntoView(true);", valores_input_but_mas)
    valores_input_but_mas.click()
    
    for j, vqd in enumerate(VQDs[1:], start=2):
        valores_input_mas = driver.find_element(By.XPATH, f'/html/body/div[1]/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[2]/div[3]/div[1]/div/metadata-filter/div/div/div/div/div[{j}]/div[2]/input[1]')
        driver.execute_script("arguments[0].scrollIntoView(true);", valores_input_mas)
        valores_input_mas.click()
        valores_input_mas.send_keys(vqd)
        sleep(2)
        if j < len(VQDs):
            valores_input_but_mas = driver.find_element(By.XPATH, f'/html/body/div[1]/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[2]/div[3]/div[1]/div/metadata-filter/div/div/div/div/div[{j}]/div[3]')
            driver.execute_script("arguments[0].scrollIntoView(true);", valores_input_but_mas)
            valores_input_but_mas.click()

def main(i, x):
    opciones = webdriver.ChromeOptions()
    opciones.add_argument('--ignore-certificate-errors') 
    opciones.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=opciones)

    driver.maximize_window()
    # Ajuste para descarga de audios sin permisos
    url_ajuste = 'chrome://settings/content/siteDetails?site=http%3A%2F%2F172.29.2.48'
    driver.get(url_ajuste)
    
    sleep(5)
    
    descargas_automatica_no_seguro(driver)
    sleep(10)
    
    print("\nFinaliza el proceso de ajuste de descargas\n")
    
    url = 'http://172.29.2.48/speechminer/pages/ui/#/explore/explore'

    driver.get(url)
    sleep(10)

    # ************ Inicio de sesion
    print("Seleccionando opcion Genesys")
    boton_genesys = driver.find_element(By.XPATH, check_gen)
    boton_genesys.click()
    sleep(1)

    print("Ingresando usuario")
    user = driver.find_element(By.XPATH, usuario)
    user.click()
    user.send_keys('p-efgarciac')
    sleep(1)

    print("Ingresando contraseña")
    password = driver.find_element(By.XPATH, contraseña)
    password.click()
    password.send_keys('14080')
    sleep(1)

    print("Iniciando sesión")
    inicio_sesion = driver.find_element(By.XPATH, boton_iniciar_sesion)
    inicio_sesion.click()

    inicio_speech = True

        
    while inicio_speech:
        try:
            buscar = driver.find_element(By.XPATH, '//span[@class = "navbar-appname ng-binding"]')
            print("Inicio de sesion Completo")
            sleep(60)
            break
        except:
            print("Cargando ventana principal")
            sleep(5)


    # ********** SELECCION DE RANGO DE FECHAS
    print("\nSeleccionando rango de fechas de seleccion de descarga")
    rango = driver.find_element(By.XPATH, rango_de_fechas)
    rango.click()
    sleep(2)

    print("Seleccionando opcion Personalizada")
    personal = driver.find_element(By.XPATH, personalizado)
    driver.execute_script("arguments[0].scrollIntoView(true);", personal)
    personal.click()
    sleep(2)

    if x == '5':
        print("Ingresando a rango de fecha De: ")
        de_rango = driver.find_element(By.XPATH, de)
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        fecha_formateada = yesterday.strftime("%m/%d/%y")
        print(fecha_formateada)
        de_rango.click()
        de_rango.send_keys(fecha_formateada)
        sleep(2)
    else:
        print("Ingresando a rango de fecha De: ")
        de_rango = driver.find_element(By.XPATH, de)
        today = datetime.datetime.now()
        fecha_formateada = today.strftime("%m/%d/%y")
        print(fecha_formateada)
        de_rango.click()
        de_rango.send_keys(fecha_formateada)
        sleep(2)
        
    print("validando el valor de x")
    print(x)
        
    # SELECCION DE PRIMER HORARIO POR HORA DE EJECUCION
    
    if x == "0":
        # PRIMER HORARIO NO HAY CAMBIO
        print("Sin cambios en el horario de la opcion De:")
        fecha_uno = driver.find_element(By.XPATH, fecha_1)
        fecha_uno.click()
        sleep(2)
        
    elif x == "1":
        # SEGUND HORARIO DE LAS 7 AM
        print("Seleccionando horario de hora 7:00 am")
        fecha_uno = driver.find_element(By.XPATH, fecha_1)
        fecha_uno.click()
        sleep(2)
        
        siet_1 = driver.find_element(By.XPATH, siete_am_1)
        driver.execute_script("arguments[0].scrollIntoView(true);", siet_1)
        siet_1.click()
        sleep(2)
        
    elif x == "2":
        # TERCER HORARIO DE LAS 1 PM
        print("Seleccionando horario inicial de hora 01:00 pm")
        fecha_uno = driver.find_element(By.XPATH, fecha_1)
        fecha_uno.click()
        sleep(2)
        
        un_1 = driver.find_element(By.XPATH, una_pm_1)
        driver.execute_script("arguments[0].scrollIntoView(true);", un_1)
        un_1.click()
        sleep(2)
    
    elif x == "3":
        # Segundo HORARIO DE LAS 1 PM
        print("Seleccionando horario inicial de hora 06:00 pm")
        fecha_uno = driver.find_element(By.XPATH, fecha_1)
        fecha_uno.click()
        sleep(2)
        
        cdmx6 = driver.find_element(By.XPATH, hora_6pm)
        driver.execute_script("arguments[0].scrollIntoView(true);", cdmx6)
        cdmx6.click()
        sleep(2)


    print("Ingresando a rango de fecha A: ")
    a_rango = driver.find_element(By.XPATH, a)
    today = datetime.datetime.now()
    fecha_formateada = today.strftime("%m/%d/%y")
    print(fecha_formateada)
    
    # Desplazarse y hacer clic usando JavaScript
    driver.execute_script("arguments[0].scrollIntoView(true);", a_rango)
    driver.execute_script("arguments[0].click();", a_rango)
    
    # Enviar la fecha formateada
    a_rango.send_keys(fecha_formateada)
    sleep(2)
    # SELECCION DE SEGUNDO HORARIO POR HORA DE EJECUCION
    
    if x == "0":
        # PRIMER HORARIO DE LAS 7 AM
        print("Seleccionando horario a hora 7:00 am")
        rango_hora_2 = driver.find_element(By.XPATH, hora_a)
        rango_hora_2.click()
        sleep(2)  
          
        siet_2 = driver.find_element(By.XPATH, siete_am_2)
        driver.execute_script("arguments[0].scrollIntoView(true);", siet_2)
        siet_2.click()
        sleep(2)
        
    elif x == "1":
        # SEGUND HORARIO DE LAS 1 PM
        print("Seleccionando horario final a hora 1:00 pm")
        rango_hora_2 = driver.find_element(By.XPATH, hora_a)
        rango_hora_2.click()
        sleep(2)    
        
        un_2 = driver.find_element(By.XPATH, una_pm_2)
        driver.execute_script("arguments[0].scrollIntoView(true);", un_2)
        un_2.click()
        sleep(2)
        
    elif x == "2":
         # TERCER HORARIO DE LAS 6 PM
        print("Seleccionando horario final a hora 6:00 pm")
        rango_hora_2 = driver.find_element(By.XPATH, hora_a)
        rango_hora_2.click()
        sleep(2)   
         
        onc_2 = driver.find_element(By.XPATH, cdmx6pm)
        driver.execute_script("arguments[0].scrollIntoView(true);", onc_2)
        onc_2.click()
        sleep(2)
        
    elif x == "3":
        # TERCER HORARIO DE LAS 11 PM
        print("Seleccionando horario final a hora 9:00 pm")
        rango_hora_2 = driver.find_element(By.XPATH, hora_a)
        rango_hora_2.click()
        sleep(2)
         
        cdmx6 = driver.find_element(By.XPATH, cdmx9pm)
        driver.execute_script("arguments[0].scrollIntoView(true);", cdmx6)
        cdmx6.click()
        sleep(2)

    # ********** SELECCION DE RANGO DE FECHAS
    
    print("\nSeleccionando hablantes")
    hablante = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/dropdown-tree/div/div/button')
    driver.execute_script("arguments[0].scrollIntoView(true);", hablante)
    driver.execute_script("arguments[0].click();", hablante)
    sleep(2)

    check_hablantes = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/dropdown-tree/div/div/div/tree-view/div/div[2]/div/span[1]')
    check_hablantes.click()
    sleep(2)
    
    hablante_2 = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[1]/div[2]/div[2]/div[2]/dropdown-tree/div/div/button')
    hablante_2.click()
    sleep(2)


    print("\nIngresando a Metadatos")
    nombre = driver.find_element(By.XPATH, nombres)
    nombre.click()

    observar = True
    while observar:
        try:
            observar_solamente = driver.find_element(By.XPATH, busqueda_meta)
            print("metadatos abierto")
            sleep(5)
            break
        except:
            print("Cargando pestaña de metadatos")
            sleep(5)

    print("Ingresando valor VQD")
    busqueda_VQD = driver.find_element(By.XPATH, busqueda)
    busqueda_VQD.click()
    busqueda_VQD.send_keys('VQD')
    sleep(2)

    checkbox_vqd = driver.find_element(By.XPATH, check_vqd_apodaca)
    checkbox_vqd.click()
    sleep(2)
    
    valor = driver.find_element(By.XPATH, valores)
    valor.click()
    sleep(2)
    
    agregar_valores_vqd(driver, i)
    sleep(2)
    
    print("Ingresando rango de tiempo de llamadas")
    duracion = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/dropdown-select/div/div/button')
    duracion.click()
    sleep(2)
    
    print("Seleccionando Opcion Entre")
    duracion_entre = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/dropdown-select/div/div/ul/li[3]')
    duracion_entre.click()
    sleep(2)
    
    print("rango 1 de 300s")
    rango_llamada_1 = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/div/input[1]')
    rango_llamada_1.click()
    sleep(2)
    rango_llamada_1.send_keys('300')
    sleep(2)
    
    print("rango 2 de 600s")
    rango_llamada_2 = driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[3]/div[3]/div/div/div[3]/div/div/form/div[1]/div[4]/div/value-range-field-search/div/div/input[2]')
    rango_llamada_2.click()
    sleep(2)
    rango_llamada_2.send_keys('600')
    sleep(2)
    
    print("Busqueda de audios iniciada")
    busqueda_ex = driver.find_element(By.XPATH, buscar_resultados)
    busqueda_ex.click()
    print("Esperando 90s para exportar")
    sleep(90)
    
    try:
        elemento_valor = driver.find_element(By.XPATH, '//span[@dir="ltr" and contains(@ng-show, "params.dataProvider.totalNumberOfResults") and contains(@class, "ng-binding")]')
        valor = elemento_valor.text.strip()
        if valor == '(0)':
            print(f"Iteración {i}: El valor es (0), saltando a la siguiente iteración")
            sleep(5)
            return
    except Exception as e:
        print(f"No se pudo encontrar el elemento en la iteración {i}: {e}")
        return

    print(f"Valor de iteracion cdmx-cuernavaca: {i}")
    print(f"Ejecutando main con i={i} y x={x}")
    
    # ********** VENTANA DE EXPORTACION
    
    fecha_hora_ex = True
    while fecha_hora_ex:
        try:
            fehca_hor = driver.find_element(By.XPATH, reconocimiento)
            print("Pagina de exportacion abierta 90s de espera")
            sleep(60)
            break
        except:
            print("Cargando ventana de exportacion")
            sleep(5)
    
    print("Click en checkbox seleccion todo")
    checkbox_select = driver.find_element(By.XPATH, check_seleccion)
    checkbox_select.click()
    sleep(2)
    
    print("Expandiendo menu de seleccion")
    exp_sel = driver.find_element(By.XPATH, expacion)
    exp_sel.click()
    sleep(2)
    
    print("Seleccionando exportar")
    expo_expo = driver.find_element(By.XPATH, expacion_exportar)
    expo_expo.click()
    sleep(20)
    
    # ********** VENTANA DE EXPORTACION MODAL 1
    
    print("\nAccediendo a ventana modal 1 seleccion de audios")

    try:
        print("Esperando a que la primer ventana modal esté visible")
        modal = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.modal.fade.ng-isolate-scope.export-modal.in'))
        )
        print("Modal está visible")
        sleep(2)

        try:
            print("Esperando a que el radio button esté visible o no encontratlo")
            radio_button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="radio"]/label[input[@type="radio" and @value="true" and @ng-value="true"]]'))
            )
            print("Radio button está clickeable")
            radio_button.click()
            print("Hicimos clic en el radio button")
        except Exception as e:
            print("Radio button no está presente o no es clickeable. Continuando sin hacer clic en el radio button.")
        
        sleep(2)
        
        print("Esperando a que el checkbox esté clickeable")
        checkbox = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="checkbox"]/label[input[@type="checkbox" and @ng-model="exportData.exportWithAudio"]]'))
        )
        print("Checkbox está clickeable")
        checkbox.click()
        print("Hicimos clic en el checkbox")
        
        sleep(2)
        
        print("Esperando a que el botón de exportar esté presente y sea clickeable")
        boton_exportar = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@translate="Explore.BatchActions.Export.ExportButton"]'))
        )
        print("Botón de exportar está presente y es clickeable")
        boton_exportar.click()
        print("Se hizo clic en el botón de exportar")
        sleep(5)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

        
        
    # ********** VENTANA DE EXPORTACION MODAL 2
    
    print("\nAccediendo a ventana modal 2 generador de contraseñas")
    
    try:
        print("Esperando a que la segunda ventana modal esté visible")
        modal = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.modal.fade.ng-isolate-scope.in'))
        )
        print("Modal está visible")

        sleep(2)
        
        print("Esperando a que el campo de contraseña esté presente y sea interactuable")
        input_contraseña = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "password-input"))
        )

        print("Campo de contraseña está presente y es interactuable")

        input_contraseña.clear()

        texto_contraseña = "Cyb*^1234567"
        input_contraseña.send_keys(texto_contraseña)
        
        sleep(2)

        print("Esperando a que el botón 'Exportar' esté presente y sea clickeable")
        boton_exportar = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@ng-if="logic.isStrongPassword()"]'))
        )

        print("Botón 'Exportar' está presente y es clickeable")

        boton_exportar.click()
        print("Se hizo clic en el botón 'Exportar'")
        
        sleep(2)
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        
    
     # ********** VENTANA DE EXPORTACION MODAL 3
    
    print("\nAccediendo a ventana modal 3 confirmacion")
    
    try:
        print("Esperando a que la tercer ventana modal esté visible")
        modal = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.modal.fade.ng-isolate-scope.in'))
        )
        print("Modal está visible")

        sleep(30)
        

        print("Esperando a que el botón 'Completado' esté presente y sea clickeable")
        boton_completado = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@translate="General.Done"]'))
        )

        print("Botón 'Completado' está presente y es clickeable")

        boton_completado.click()
        print("Se hizo clic en el botón 'Completado'")
        
        sleep(1800)
        
        usu_cierre = driver.find_element(By.XPATH, user_cierre)
        usu_cierre.click()
        sleep(3)

        cierre_final = driver.find_element(By.XPATH, cierre)
        cierre_final.click()
        sleep(90)
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        driver.quit()
    
    if i == 0:
        i = 3
        print("Nuevo valor de i: ", i)
    elif i == 1:
        i = 4
        print("Nuevo valor de i: ", i)
    
    print("\nIniciando extraccion de archvio zip")
    subprocess.run(["python", "extraccion_archivos.py", str(i)])
    sleep(2)
    
    print("\nIniciando movimiento y renombramiento de archivos de audio")
    subprocess.run(["python", "mover_renombrar.py", str(i)])
    sleep(2)
    
    print("\nIniciando carga a la base de datos")
    subprocess.run(["python", "carga_base.py", str(i)])
    sleep(2)
    
    print("\nIniciando eliminacion de carga de audios")
    subprocess.run(["python", "eliminar_rar.py"])
    sleep(2)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        x = sys.argv[1]
        # x = 1
        if x == "0":
            print("\nEjecucion de las 7 am")
        elif x == "1":
            print("\nEjecucion de las 1 pm")
        elif x == "2":
            print("\nEjecucion de las 5 pm")
        elif x == "3":
            print("\nEjecucion de las 8 pm")
        elif x == "4":
            print("\nEjecucion de las 11 pm")
        elif x == "5":
            print("\nEjecucion de las 12 am")
        
        for i in range(2):
            print("\nValor de iteracion apodaca: ", i)
            main(i, x)
    else:
        print("Por favor, proporciona el nombre del archivo como argumento de línea de comandos.")
    
