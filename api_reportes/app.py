from flask import Flask, render_template, request,redirect,url_for,send_file
from flask import jsonify
import time
from flask_cors import CORS, cross_origin
from flask_mysqldb import MySQL
import requests
from peticiones import *

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
    # x = requests.get('http://127.0.0.1:5000/investigadores')
    # print(x.text)
    return 'API REPORTES- WEB SCRAPING - GOOGLE SCHOLAR'

@app.route('/reporte_investigador/<id>')
def obtener_reporte(id):

    reporte_investigador(id)
    
    try:
        return send_file('investigador.xlsx')
    except Exception as e:
        print(str(e))
        return jsonify({"mensaje":"error"})

@app.route('/reporte_investigadores',methods=['POST'])
def obtener_reporte_ids():
    body = request.json['body']
    body = json.loads(body)
    print(body)
    lista_ids = body['ids']
    print(lista_ids)

    if len(lista_ids)>0:
        reporte_investigadores(lista_ids,False)
    else:
        reporte_investigadores(lista_ids,True)

    try:
        return send_file('investigadores.xlsx')
    except Exception as e:
        print(str(e))
        return jsonify({"mensaje":"error"})
if __name__ == '__main__':
    app.run(debug=True,port=4000)