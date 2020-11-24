from flask import Flask, render_template, request,redirect,url_for,flash
from flask import jsonify
import time
import ws
from flask_cors import CORS, cross_origin
from flask_mysqldb import MySQL

app = Flask(__name__)

# Mysql connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'bd_ws'

# settings
app.secret_key = 'mysecretkey'

mysql = MySQL(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def index():
    return 'API - WEB SCRAPING - GOOGLE SCHOLAR'

@app.route('/investigadores')
def obtener_investigadores():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM investigador')
    investigadores_obtenidos  =  cur.fetchall()
    investigadores_resp = []
    for investigador in investigadores_obtenidos:
        investigador_dict = {"idinvestigador":investigador[0],
         "nombres":investigador[1],
         "informacion":investigador[2],
         "url_imagen":investigador[3],
         "url_perfil":investigador[4]}

        #obtener los topicos
        cur.execute('SELECT topico FROM topico WHERE investigador_idinvestigador = {}'.format(investigador_dict['idinvestigador']))
        topicos_obtenidos  =  cur.fetchall()
        topicos = [topico[0] for topico in topicos_obtenidos]

        investigador_dict['topicos'] = topicos

        investigadores_resp.append(investigador_dict)

    return jsonify({'investigadores':investigadores_resp,"status":200})

@app.route('/investigador/<id>')
def obtener_investigador(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM investigador WHERE idinvestigador = {}'.format(id))
    investigador = cur.fetchone()
    
    if investigador :
        # recuperar topicos
        cur.execute('SELECT topico FROM topico WHERE investigador_idinvestigador = {}'.format(id))
        topicos_obtenidos  =  cur.fetchall()
        topicos = [topico[0] for topico in topicos_obtenidos]

        # recuperar investigaciones
        cur.execute('SELECT * FROM investigacion WHERE investigador_idinvestigador = {}'.format(id))
        investigaciones_obtenidas  =  cur.fetchall()
        investigaciones_resp = []
        for investigacion in investigaciones_obtenidas:
            investigacion_dict = {
                "idinvestigacion":investigacion[0],
                "titulo":investigacion[1],
                "revista":investigacion[2],
                "autores":investigacion[3],
                "anio":investigacion[4],
                "numero_citaciones":investigacion[5],
                "idinvestigador":investigacion[6]}
            investigaciones_resp.append(investigacion_dict)

        # recuperar citaciones
        cur.execute('SELECT * FROM cita WHERE investigador_idinvestigador = {}'.format(id))
        citas_obtenidas  =  cur.fetchall()
        citas_resp = []
        for cita in citas_obtenidas:
            cita_dict = {
                "idcita":cita[0],
                "modalidad":cita[1],
                "desde_2015":cita[2],
                "total":cita[3],
                "idinvestigador":cita[4]}
            citas_resp.append(cita_dict)


        return jsonify(
            {
                "investigador":{
                    "idinvestigador":investigador[0],
                    "nombres":investigador[1],
                    "informacion":investigador[2],
                    "url_imagen":investigador[3],
                    "url_perfil":investigador[4],
                    "topicos":topicos,
                    "investigaciones":investigaciones_resp,
                    "citas":citas_resp},
                "status":200})
    else:
        return jsonify({"mensaje":"investigador no encontrado",
        "status":500})

@app.route('/investigador',methods=['POST'])
def agregar_investigador():
    if request.method == 'POST':
        url = request.form['url']

        url = url.strip()

        #verificar que no hayan duplicados
        cur = mysql.connection.cursor()
        query_select = "SELECT '{}' in (select url_perfil from investigador);".format(url)
        print("query_select: ", query_select)
        cur.execute(query_select)
        existe_inv = cur.fetchone()
        existe_inv = existe_inv[0]

        if existe_inv == 1:
            print("Ya existe el investigador")
            return jsonify({"respuesta":"Ya existe el investigador","status":500})

        try:
            investigador= ws.obtener_datos_investigador(url)

            # ingresando investigador
            cur = mysql.connection.cursor()
            script_insert ="INSERT INTO investigador (nombres,informacion,url_imagen,url_perfil) VALUES ('{}','{}','{}','{}')".format(
                investigador['nombres'],
                investigador['informacion'],
                investigador['url_imagen'],
                investigador['url_perfil'])
            
            print('script_insert: ',script_insert)
            cur.execute(script_insert)
            mysql.connection.commit()

            #obtenemos el id del investigador que ingresamos

            cur = mysql.connection.cursor()
            query_select = "SELECT MAX(idinvestigador) from investigador;"
            cur.execute(query_select)
            id_investigador = cur.fetchone()
            id_investigador = id_investigador[0]
            print('query_select: ',query_select)
            print('id_investigador: ',id_investigador)

            # ingresando topicos
            for topico in investigador['topicos']:
                cur = mysql.connection.cursor()
                script_insert ="INSERT INTO topico (topico,investigador_idinvestigador) VALUES ('{}',{})".format(
                    topico,
                    id_investigador)
                print('script_insert: ',script_insert)
                cur.execute(script_insert)
                mysql.connection.commit()

            # ingresando investigaciones
            for investigacion in investigador['lista_investigaciones']:
                cur = mysql.connection.cursor()
                if investigacion['numero_citaciones'] == '':
                    investigacion['numero_citaciones'] = 0
                if investigacion['año'] == '':
                    investigacion['año'] = 0

                # citaciones*
                numero_citas = investigacion['numero_citaciones']
                numero_citas = str(numero_citas)
                while True:
                    if numero_citas.isnumeric():
                        break
                    else:
                        numero_citas = numero_citas[:-1]
                investigacion['numero_citaciones'] = numero_citas

                script_insert ='INSERT INTO investigacion (titulo,revista,autores,año,numero_citaciones,investigador_idinvestigador) VALUES ("{}","{}","{}",{},{},{})'.format(
                    investigacion['titulo'],
                    investigacion['revista'],
                    investigacion['autores'],
                    investigacion['año'],
                    investigacion['numero_citaciones'],
                    id_investigador)
                print('script_insert: ',script_insert)
                cur.execute(script_insert)
                mysql.connection.commit() 

            #ingresando citas
            citaciones = investigador['citaciones']

            for k,v in citaciones.items():
                cur = mysql.connection.cursor()
                script_insert ="INSERT INTO cita (modalidad,desde_2015,total,investigador_idinvestigador) VALUES ('{}',{},{},{})".format(
                    k,
                    v['Desde 2015'],
                    v['Total'],
                    id_investigador)

                print('script_insert: ',script_insert)
                cur.execute(script_insert)
                mysql.connection.commit()

            investigador['id'] = id_investigador

            # print(citaciones)

            response = {
                "respuesta":"Se agregó satisfactoriamente al investigador",
                "status":200,
                "investigador":investigador
            }
        except Exception as e:
            print(e)
            response = {
                "respuesta":"Error",
                "status":500
            }
        return jsonify(response)

@app.route('/ws_investigador',methods=['POST'])
def obtener_datos_investigador():
    if request.method == 'POST':
        url = request.form['url']
        investigador= ws.obtener_datos_investigador(url)

        response = {
            "investigador":investigador
        }

        return jsonify(response)

@app.route('/busqueda',methods=['POST'])
def buscar_investigadores():
    if request.method == 'POST':
        nombres = request.form['nombres']
        respuesta = ws.buscar_investigador(nombres)

        return jsonify({"respuesta":respuesta})

if __name__ == '__main__':
    app.run(debug=True,port=5000)