from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import numpy as np
import pandas as pd


#obtener citaciones
def obtener_citaciones(url_source,as_df=False,is_url=True):

  if is_url:
    response=requests.get(url_source)
    soup=BeautifulSoup(response.content,'lxml')
  else:
    soup=BeautifulSoup(url_source,'lxml')

  # primera tabla - tabla de citaciones
  tablas = soup.find_all('table')
  matriz_citaciones=[]

  # extraemos las cabeceras de la tabla
  cabeceras_tabla = []
  headers_tabla = tablas[0].find('thead')
  cabeceras_tabla = [campo.text for campo in headers_tabla.find_all('th') if len(campo.text)> 0]
  cabeceras_tabla =['']+cabeceras_tabla

  # guardamos la primera fila en la matriz de citaciones
  matriz_citaciones.append(cabeceras_tabla)

  # cuerpo de la tabla
  cuerpo_tabla = tablas[0].find('tbody')
  for row in cuerpo_tabla.find_all('tr'):
    temp_lista = []
    for col in row.find_all('td'):
      temp_lista.append(col.text)
    # guaradamos cada fila en la matriz de citaciones
    matriz_citaciones.append(temp_lista)

  df = pd.DataFrame(matriz_citaciones)
  df = df.rename(columns=df.iloc[0])
  df.drop(0,inplace=True)
  df = df.set_index('')
  
  if as_df:
    return df
  else:
    return df.to_dict(orient="index")

#obtener investigaciones
def scrapear_data(url_source,as_df=False,is_url=True):
  if is_url:
    response=requests.get(url_source)
    soup=BeautifulSoup(response.content,'lxml')
  else:
    soup=BeautifulSoup(url_source,'lxml')

  lista_investigaciones = []

  for elem in soup.find_all('tr', attrs={'class':'gsc_a_tr'}):
    paper = elem.find('a')
    nombre_paper = paper.text

    # encontrando autores y revista
    desc = elem.find_all('div',attrs={'class':'gs_gray'})
    autores = desc[0].text
    revista = desc[1].text

    # numero de citaciones
    num_citaciones = elem.find('td',attrs={'class':'gsc_a_c'}).text

    # año
    año = elem.find('td',attrs={'class':'gsc_a_y'}).text

    investigaciones = {
        'titulo':nombre_paper,
        'autores': autores,
        'revista': revista,
        'numero_citaciones':num_citaciones,
        'año':año
    }
    # print(investigaciones)
    lista_investigaciones.append(investigaciones)

  if as_df:
    return pd.DataFrame(lista_investigaciones)
  else:
    return lista_investigaciones

#OBTIENE EL PERFIL DE UN INVESTIGADOR
def obtener_perfil(url_source,is_url=True):
    if is_url:
        response=requests.get(url_source)
        soup=BeautifulSoup(response.content,'lxml')
    else:
        soup=BeautifulSoup(url_source,'lxml')
   
    investigador = soup.find("div",{"id":"gsc_prf"})

    #url imagen
    imagen_investigador = investigador.find("img")
    url_imagen = imagen_investigador['src']
    
    #nombres
    nombres = investigador.find("div",{"id":"gsc_prf_in"}).text
    
    #afiliacion
    afiliacion = investigador.find("div",{"class":"gsc_prf_il"}).text
    
    #topicos
    topicos = investigador.find("div",{"id":"gsc_prf_int"})
    topicos = [topico.text for topico in topicos]

    return {
        "url_imagen":url_imagen,
        "nombres":nombres,
        "afiliacion":afiliacion,
        "topicos":topicos}

#OBTIENE TODOS LOS DATOS DE UN INVESTIGADOR
def obtener_datos_investigador(url):
    
    # response=requests.get(url)
    # soup=BeautifulSoup(response.content,'lxml')
      
    # investigador = soup.find("div",{"id":"gsc_prf"})

    # #url imagen
    # imagen_investigador = investigador.find("img")
    # url_imagen = imagen_investigador['src']
    
    # #nombres
    # nombres = investigador.find("div",{"id":"gsc_prf_in"}).text
    
    # #cargo
    # cargo = investigador.find("div",{"class":"gsc_prf_il"}).text
    
    # #topicos
    # topicos = investigador.find("div",{"id":"gsc_prf_int"})
    # topicos = [topico.text for topico in topicos]

    
    
    ## agregamos selenium
    PATH = 'C:\Program Files (x86)\chromedriver.exe'
    driver = webdriver.Chrome(PATH)

    driver.get(url)
    
    cont=0
    try:
        # click en cargar más
        while True:
            boton = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "gsc_bpf_more"))
            )
            
            if boton.is_enabled():
                boton.click()
                cont+=1
                boton=[]
            else:
                break
            time.sleep(1)

        
            
        print("{} clicks".format(cont))
        investigaciones = driver.find_elements_by_class_name('gsc_a_tr')
        print("Investiaciones encontradas-selenium: {}".format(len(investigaciones)))

        #perfil
        perfil = obtener_perfil(driver.page_source,is_url=False)

        #lista de investigaciones
        lista_investigaciones = scrapear_data(driver.page_source,as_df=False,is_url=False)
        print("Investigaciones encontradas-beautifoulsoup: {}".format(len(lista_investigaciones)))
        
        #citaciones
        citaciones = obtener_citaciones(driver.page_source,as_df=False,is_url=False)
    
        return {'url_perfil':url,
                'nombres':perfil['nombres'],
                'informacion': perfil['afiliacion'],
                'topicos':perfil['topicos'],
                'url_imagen':perfil['url_imagen'],
                'lista_investigaciones': lista_investigaciones,
                'citaciones': citaciones
                }

    finally:
        driver.quit()

#OBTIENE DATOS DE MULTIPLES INVESTIGADORES
def obtener_datos_investigadores(lista_urls):
    lista_investigadores = []

    for url in lista_urls:
        investigador = obtener_datos_investigador(url)
        lista_investigadores.append(investigador)

    return lista_investigadores

#BUSCA INVESTIGADORES POR NOMBRE
def buscar_investigador(nombres):

    # enviamos los nombres
    url_source = "https://scholar.google.com/scholar?hl=es&as_sdt=0%2C5&q={}&btnG=&oq=".format(nombres)

    url_base = "https://scholar.google.com"

    try:
        # request a google scholar 
        response=requests.get(url_source)
        soup=BeautifulSoup(response.content,'lxml')

        main = soup.find("div",{"class":"gs_r"})

        investigadores=[]

        #autores 
        for div in main.find_all('h4'):
            a = div.find('a')
            href = a['href']
            href = href.split("=")

            id = href[1]
            id = id[:-3]


            url_perfil = "{}/citations?user={}&hl=es&oi=ao".format(url_base,id)
            print(url_perfil)

            investigador = obtener_perfil(url_perfil)

            investigador['url_perfil'] = url_perfil
            investigadores.append(investigador)
        
        return investigadores
    except Exception as e:
        print(e)
        print("No se encontraron investigadores")
        return []

# print(buscar_investigadores('moq'))
# print(scrapear_data('https://scholar.google.com/citations?user=CDt8mKsAAAAJ&hl=es&oi=ao',as_df=False,is_url=True))

#obtener los datos de un investigador
# print(obtener_datos_investigador('https://scholar.google.com/citations?user=CDt8mKsAAAAJ&hl=es&oi=ao'))

#obtener datos de varios investigadores
# autores_urls = ['https://scholar.google.com/citations?user=CDt8mKsAAAAJ&hl=es&oi=ao',#prof moquillaza
# 'https://scholar.google.com/citations?user=c9ZEN0YAAAAJ&hl=es&oi=ao']#prof guerra

# print(buscar_investigador("moquillaza"))