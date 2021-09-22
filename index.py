from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_file
from functools import wraps
import numpy as np
from passlib.hash import pbkdf2_sha256
import logging
import json


def Get():
  return []

def GetLastDate(jsonData):
  return jsonData['lastProcces']

def Filtrar(empresa, periodo, jsonData):
  return [x for x in jsonData['empresas'] if (empresa == '' or x['id'] == empresa) and (periodo == '' or x['periodo'] == periodo)]

FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
logging.basicConfig(level=logging.DEBUG,format=FORMAT)


# initializations
app = Flask(__name__, static_url_path='/static')

# Variables de App
app.config['admin'] = '$pbkdf2-sha256$29000$lHKOEaJ0TqlVao3RmpMyxg$PBZlqFkDiSIY5uDQ7RV8UZDcwJdyhDohxXCwZCou3vQ'

# settings
app.secret_key = "df2-sha256$29000$lHKOEaJ0T"

try:
    with open("repo/data.json", "r") as file:
      app.config['data'] = json.load(file)
      logging.debug(app.config['data'] )
except Exception as exp:
    logging.critical("ERROR EN LOAD LAST JSON")
    logging.exception(exp)


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")

# Decorators - Es como un ESB
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      flash('Debe ingresar usuario y clave')
      return redirect('/')
  
  return wrap

# routes Default con Login obligatorio
@app.route('/')
def default():
  return render_template('login.html')

# Login 
@app.route('/login/', methods=['POST'])
def login():
  if request.form.get('user') == 'admin' and pbkdf2_sha256.verify(request.form.get('password'), app.config['admin']):
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    session['logged_in'] = True
    return redirect(url_for('dashboard'))
  else:
      flash('Usuario y Clave invalido')
      return redirect(url_for('default'))

# Cerrar Session
@app.route('/signup', methods=['POST'])
def signup():
  session.clear()
  return redirect(url_for('default'))

# Panel de consulta
@app.route('/dashboard')
@login_required
def dashboard():
  return render_template('mayorexport.html', contacts = Get(), fecha=GetLastDate(app.config['data']))

# Filtrar Datos.
@app.route('/filtrar', methods = ['POST'])
@login_required
def filtrar():
  return render_template('mayorexport.html', contacts = Filtrar(request.form['empresa'],request.form['periodo'],app.config['data']), fecha=GetLastDate(app.config['data']))

# Download export.
@app.route('/download/<string:filename>', methods = ['GET'])
@login_required
def download(filename):
    try:
        logging.debug('Download file: {}'.format(filename))
        return send_file(('repo/'+filename), mimetype='application/zip', attachment_filename=filename, as_attachment=True)

    except Exception as exp:
        logging.critical("Archivo no encontrado {}".format(filename))
        logging.exception(exp)
        flash('Archivo no encontrado, reintiento o contacte al administrador {}'.format(filename))
        return redirect(url_for('dashboard'))
  

# starting the app
if __name__ == "__main__":
#  app.run(port=80, debug=false)
  app.run()
