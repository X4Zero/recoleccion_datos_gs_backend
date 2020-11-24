import os
import requests
import numpy as np
import pandas as pd
import json

def reporte_investigadores(lista_ids,todos=True):

    if todos:
        #obtenemos todos los investigadores
        respuesta = requests.get('http://127.0.0.1:5000/investigadores')
        resp = json.loads(respuesta.text)
        lista_res= resp['investigadores']

        lista_ids = [res['idinvestigador'] for res in lista_res]

    lista_investigadores = []
    for id in lista_ids:
        respuesta = requests.get('http://127.0.0.1:5000/investigador/{}'.format(id))
        resp = json.loads(respuesta.text)

        inv = resp['investigador']

        #dataframe perfil
        #citas
        citas = inv['citas']
        numero_citas = 0
        indice_h = 0
        indice_i10 = 0
        for cita  in citas:
            if cita['modalidad'] == 'Citas':
                numero_citas = cita['total']
            if cita['modalidad'] == 'Índice h':
                indice_h = cita['total']
            if cita['modalidad'] == 'Índice i10':
                indice_i10 = cita['total']

        investigador_informacion = {
            "nombres": inv['nombres'],
            "afiliacion": inv['informacion'],
            "citas":numero_citas,
            "índice h":indice_h,
            "índice i10":indice_i10,
            "url_perfil": inv['url_perfil'],
            "url_imagen": inv['url_imagen'],
            "intereses": ",".join(inv['topicos'])
        }
        lista_investigadores.append(investigador_informacion)

    df = pd.DataFrame(lista_investigadores)
    df.loc[~df['url_imagen'].str.contains('http',regex=False),'url_imagen'] = ''
    # print(df)

    with pd.ExcelWriter('investigadores.xlsx') as writer:  
        df.to_excel(writer, sheet_name='investigadores',index=False)

def reporte_investigador(id):
    respuesta = requests.get('http://127.0.0.1:5000/investigador/{}'.format(id))
    resp = json.loads(respuesta.text)

    inv = resp['investigador']

    #dataframe perfil
    #citas
    citas = inv['citas']
    numero_citas = 0
    indice_h = 0
    indice_i10 = 0
    for cita  in citas:
        if cita['modalidad'] == 'Citas':
            numero_citas = cita['total']
        if cita['modalidad'] == 'Índice h':
            indice_h = cita['total']
        if cita['modalidad'] == 'Índice i10':
            indice_i10 = cita['total']

    investigador_informacion = {
        "nombres": inv['nombres'],
        "afiliacion": inv['informacion'],
        "citas":numero_citas,
        "índice h":indice_h,
        "índice i10":indice_i10,
        "url_perfil": inv['url_perfil'],
        "url_imagen": inv['url_imagen'],
        "intereses": ",".join(inv['topicos'])
    }

    df_perfil = pd.DataFrame([investigador_informacion])
    df_perfil = df_perfil.transpose()
    print(df_perfil)
    df_perfil.columns=['Datos']

    #dataframe investigaciones
    lista_investigaciones = inv['investigaciones']

    df_investigaciones = pd.DataFrame(lista_investigaciones)
    df_investigaciones['año'] = df_investigaciones['anio']
    df_investigaciones.drop('anio',axis=1,inplace=True)

    df_investigaciones_exp = df_investigaciones.iloc[:,5:]
    df_investigaciones_exp['autores'] = df_investigaciones['autores']
    df_investigaciones_exp['revista'] = df_investigaciones['revista']
    df_investigaciones_exp['Número de citaciones'] = df_investigaciones['numero_citaciones']

    # print(df_investigaciones)

    with pd.ExcelWriter('investigador.xlsx') as writer:  
        df_perfil.to_excel(writer, sheet_name='Investigador')
        df_investigaciones_exp.to_excel(writer, sheet_name='Investigaciones',index=False)



    # print(resp)
# reporte_investigadores()
# reporte_investigadores([1,3],False)
# reporte_investigadores([],True)
# reporte_investigador(1)