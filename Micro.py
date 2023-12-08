import difflib
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import serial  # Agregar esta línea

def comparar_documentos(doc1, doc2):
    diff = difflib.SequenceMatcher(None, doc1, doc2)
    similarity_ratio = diff.ratio()
    return similarity_ratio

def buscar_documento(query):
    driver = webdriver.Chrome()
    
    driver.get("https://scholar.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    driver.implicitly_wait(10)

    result_links = driver.find_elements(By.CSS_SELECTOR, ".gs_rt a")
    if result_links:
        result_links[0].click()
        contenido_documento = driver.page_source
    else:
        print(f"No se encontraron resultados en Google Académico para la búsqueda: {query}")
        contenido_documento = ""

    driver.quit()
    
    return contenido_documento

def normalizar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

# Crear una ventana de tkinter para seleccionar el archivo PDF
root = tk.Tk()
root.withdraw()

pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

with open(pdf_file_path, 'rb') as pdf_file:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    contenido_documento1 = ''

    for page in pdf_reader.pages:
        page_text = page.extract_text()
        contenido_documento1 += page_text

# Configuración de la comunicación serial con Arduino
ser = serial.Serial('COM2', 9600)  # Ajusta el puerto COM según tu configuración

# Realizar la búsqueda y comparación con 5 documentos diferentes
for i in range(5):
    query_documento2 = ' El Edipo de David Guterson: convergencia y travestismo ' + str(i+1)  # Cambiar el query de búsqueda aquí

    contenido_documento2 = buscar_documento(query_documento2)

    if contenido_documento1 and contenido_documento2:
        contenido_documento1 = normalizar_texto(contenido_documento1)
        contenido_documento2 = normalizar_texto(contenido_documento2)

        similitud = comparar_documentos(contenido_documento1, contenido_documento2)

        if similitud > 0.0000000000000000001:
            print(f"Comparación {i + 1}: Los documentos son similares. Puede haber plagio.")
            print(f"Similitud: {similitud * 100}%")
            ser.write(b'1')  # Envia '1' por la comunicación serial
        else:
            print(f"Comparación {i + 1}: Los documentos no son similares. No hay plagio detectado.")
            print(f"Similitud: {similitud * 100}%")
            ser.write(b'0')  # Envia '0' por la comunicación serial
    else:
        print(f"Comparación {i + 1}: No se pudieron obtener los documentos para comparar.")

# Cierra la conexión serial
ser.close()
