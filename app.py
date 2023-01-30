from fileinput import filename
import imp
from optparse import Values
from select import select
from sqlite3 import connect
from xmlrpc.client import boolean
from flask import Flask, before_render_template, render_template, request, url_for, redirect, abort, flash, session, jsonify, g, current_app, escape, Response
from werkzeug.wrappers.response import ResponseStream
from email.message import EmailMessage
import mysql.connector
from datetime import date, datetime
import time
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flaskext.mysql import MySQL
import pymysql
from fpdf import FPDF
import re
import os
from werkzeug.utils import secure_filename

from flask_mail import Mail
mail = Mail()

#----------------------------------------
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_cors import CORS

#----------------------------------------

#----------------------------------------
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
#----------------------------------------



class User:
    def __init__(self, id, nombre, apellido, rut,telefono, direccion, correo, password):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.rut = rut
        self.telefono = telefono
        self.direccion = direccion
        self.correo = correo
        self.password = password

    def __repr__(self):
        return f'{self.rut}'

class Func:
    def __init__(self, id, rut, nombre, apellido, correo, password, rol):
        self.id = id
        self.rut = rut
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.password = password
        self.rol = rol

    def __repr__(self):
        return f'{self.rut}'

app = Flask(__name__)

CORS(app)


api_key = 'AIzaSyBMKM8EL_YX9zrh0JgSzY7O-A6bnr--r_M'
GoogleMaps(app, key = api_key)
devices_data = {} 
devices_location = {}



midb = mysql.connector.connect(
    host="localhost",
    user='root',
    password='1234',
    database='app_cafe',
    buffered =True
)

app.secret_key = 'my secret key'

cursor = midb.cursor(dictionary=True)

# **************************************
# PARA MANEJAR CARRO DE COMPRAS
# **************************************
carro = []
precio_total = []
tabla_reporte_prod = []
tabla_reporte_aud = []
# **************************************


# CARPETA IMAGENES
app.config['cargar_imagen'] = 'static/alimentos'


# ***************************************************************************************
# PARA MANEJAR INICIO DE SESION
# ***************************************************************************************
users = []

cursor.execute("SELECT * FROM funcionario")
funcionarios = cursor.fetchall()
for f in funcionarios:
    users.append(Func(id=f['id'], rut=f['rut'], nombre=f['nombre'], apellido=f['apellido'], correo=f['correo'], password=f['password'], rol=f['rol'] ))

cursor.execute("SELECT * FROM cliente")
clientes = cursor.fetchall()
for c in clientes:
    users.append(User(id=c['id'], nombre=c['nombre'], apellido=c['apellido'], rut=c['rut'], telefono=c['telefono'], direccion=c['direccion'], correo=c['correo'], password=c['password']))
# ***************************************************************************************

# ***************************************************************************************
@app.before_first_request
def borrar_usuario():
    session.pop('user_id', None)
    session.pop('tipo', None)

@app.before_request
def load_user():
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']]
        g.user = user
# ***************************************************************************************






#---------- HOME -----------
@app.route('/')
def index():

    if 'user_id' not in session:
        return render_template('home.html', cliente = None)
    else:
        cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
        cliente = cursor.fetchone()
        return render_template('home.html', cliente = cliente)    





#---------- REGISTRO Y LOGIN ----------------------
#---------- PAGINA TU CUENTA ----------------------
@app.route('/tu_cuenta', methods=['POST', 'GET'])
def tu_cuenta():

    if 'user_id' not in session:
        return render_template('tu_cuenta.html', cliente = None, funcionario = None)

    else:
        if '_flashes' in session:
            if 'user_id' not in session:
                return render_template('tu_cuenta.html', cliente = None, funcionario = None)

            else:
                
                if session['tipo'] == 1:
                    cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
                    cliente = cursor.fetchone()

                    if cliente == None:
                        return render_template('tu_cuenta.html', cliente = None, funcionario = None)

                    cursor.execute("SELECT * FROM pedido WHERE id_cliente = '%s'" %cliente['id'] )
                    pedidos = cursor.fetchall()

                    z = 0
                    while z < len(pedidos):
                        cursor.execute("SELECT * FROM pedido_producto WHERE id_pedido = {0}".format(pedidos[z]['id'] ))
                        pedido_producto = cursor.fetchall()

                        x = 0
                        nombre_producto = ''

                        while x < len(pedido_producto):
                            cursor.execute("SELECT * FROM producto WHERE id = {0}".format(pedido_producto[x]['id_producto'] ))
                            producto = cursor.fetchone()                
                            if nombre_producto == '':
                                nombre_producto = producto['nombre']
                            else:
                                nombre_producto = nombre_producto + ' - ' + producto['nombre']

                            x += 1   
                        pedidos[z]['nombres'] = nombre_producto


                        cursor.execute("SELECT * FROM sucursal WHERE id = {0}".format(pedidos[z]['id_sucursal']))
                        sucursal = cursor.fetchone()
                        pedidos[z]['sucursal'] = sucursal['direccion']
                        z += 1

                    return render_template('tu_cuenta.html', cliente = cliente, pedidos=pedidos, funcionario = None)

                else:
                    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id'] ))
                    funcionario = cursor.fetchone()
                    return render_template('tu_cuenta.html', cliente = None, funcionario=funcionario)

        else:
            if session['tipo'] == 1:
                cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
                cliente = cursor.fetchone()

                if cliente == None:
                    return render_template('tu_cuenta.html', cliente = None, funcionario = None)

                cursor.execute("SELECT * FROM pedido WHERE id_cliente = '%s'" %cliente['id'] )
                pedidos = cursor.fetchall()

                z = 0
                while z < len(pedidos):
                    cursor.execute("SELECT * FROM pedido_producto WHERE id_pedido = {0}".format(pedidos[z]['id'] ))
                    pedido_producto = cursor.fetchall()

                    x = 0
                    nombre_producto = ''

                    while x < len(pedido_producto):
                        cursor.execute("SELECT * FROM producto WHERE id = {0}".format(pedido_producto[x]['id_producto'] ))
                        producto = cursor.fetchone()                
                        if nombre_producto == '':
                            nombre_producto = producto['nombre']
                        else:
                            nombre_producto = nombre_producto + ' - ' + producto['nombre']

                        x += 1   
                    pedidos[z]['nombres'] = nombre_producto


                    cursor.execute("SELECT * FROM sucursal WHERE id = {0}".format(pedidos[z]['id_sucursal']))
                    sucursal = cursor.fetchone()
                    pedidos[z]['sucursal'] = sucursal['direccion']
                    z += 1

                return render_template('tu_cuenta.html', cliente = cliente, pedidos=pedidos, funcionario = None)

            else:
                cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id'] ))
                funcionario = cursor.fetchone()
                return render_template('tu_cuenta.html', cliente = None, funcionario=funcionario)

#------------  INICIAR SESION ---------------
@app.route('/iniciar_sesion', methods=['POST', 'GET'])
def iniciar_sesion():
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('tipo', None)

        users = []
        cursor.execute("SELECT * FROM cliente")
        clientes = cursor.fetchall()
        cursor.execute("SELECT * FROM funcionario")
        funcionarios = cursor.fetchall()

        for c in clientes:
            users.append(User(id=c['id'], nombre=c['nombre'], apellido=c['apellido'], rut=c['rut'], telefono=c['telefono'], direccion=c['direccion'], correo=c['correo'], password=c['password']))
    
        for f in funcionarios:
            users.append(Func(id=f['id'], rut=f['rut'], nombre=f['nombre'], apellido=f['apellido'], correo=f['correo'], password=f['password'], rol=f['rol'] ))


        correo = request.form['correo']
        password = request.form['password']
        tipo = request.form.get('tipo', type=int)
        
        # TIPO IGUAL A CLIENTE 
        if tipo == 1:
            cursor.execute("SELECT * FROM cliente WHERE correo = '%s'" %correo)
            cliente = cursor.fetchone()
            if cliente != None:
                user = [x for x in users if x.correo == correo][0]             

                if user and user.password == password:
                    session['user_id'] = user.id
                    session['tipo'] = 1
                    return redirect(url_for('index'))
                
                flash('El correo y/o el password son incorrectos')
                return redirect(url_for('tu_cuenta'))
            else:
                flash('El correo y/o el password son incorrectos')
                return redirect(url_for('tu_cuenta'))        
        
        # TIPO IGUAL A FUNCIONARIO
        else:
            cursor.execute("SELECT * FROM funcionario WHERE correo = '%s'" %correo)
            funcionario = cursor.fetchone()

            if funcionario != None:

                if funcionario['estado'] == 0:
                    flash('El funcionario se encuentra desactivado')
                    return redirect(url_for('tu_cuenta'))
                else:
                    user = [x for x in users if x.correo == correo][0]
                    if user and user.password == password:
                        session['user_id'] = user.id
                        session['tipo'] = 2
                        if funcionario['rol'] == 1:
                            return redirect(url_for('admin_personal'))
                        else:
                            return redirect(url_for('admin_pedidos'))

                    flash('El correo y/o el password son incorrectos')
                    return redirect(url_for('tu_cuenta'))
            else:
                flash('El correo y/o el password son incorrectos')
                return redirect(url_for('tu_cuenta'))    

#---------- REGISTRARSE -----------
@app.route('/registrarse', methods=['POST', 'GET'])
def registrarse():
    if request.method == 'POST':
        session.pop('user_id', None)
        session.pop('tipo', None)

        cursor.execute('SELECT * FROM cliente')
        clientes = cursor.fetchall()
        mayor = 0

        for cliente in clientes:
            if mayor == 0:
                mayor = cliente['id']
            else:
                mayor = cliente['id'] if cliente['id'] > mayor else mayor

        id = mayor + 1
        nombre = request.form.get('nombre', type=str).capitalize()
        apellido = request.form.get('apellido', type=str).capitalize()
        rut = request.form.get('rut', type=str).capitalize()
        telefono = request.form.get('telefono', type=int)
        direccion = request.form.get('direccion', type=str)
        correo = request.form.get('correo', type=str)
        password = request.form.get('password', type=str)
        r_password = request.form.get('r_password', type=str)
        estado = True

        #validar rut
        # ------------------------------------------------
        i=0
        if rut.count('-') != 1 or rut.count('k') > 1:
            i = 2
        else:
            if len(rut) == 10:
                if rut.find('k') == -1 or rut.find('k') == 9:
                    if rut.find('-') != 8:
                        i = 2
                else:
                    i = 2
            
            elif len(rut) == 9:
                if rut.find('k') == -1 or rut.find('k') == 8:
                    if rut.find('-') != 7:
                        i = 2
                else:
                    i = 2
            else:
                i = 2
        # ------------------------------------------------

        
        
        # VALIDAR CORREO ELECTRONICO
        # ------------------------------------------------

        emailRegex = r'(^[\w]+)@([\w]+)' + '.com'
        match = re.search(emailRegex, correo)
        if match:
            print("valido")
        else:
            i  = 3

        # ------------------------------------------------



        for c in clientes:
            if c['rut'] ==  rut:
                i += 1

        if i == 1:
            flash('Este usuario ya existe')
            return redirect(url_for('tu_cuenta'))
        if i == 2:
            flash('El rut no es valido')
            return redirect(url_for('tu_cuenta'))
        if i == 3:
            flash('El correo no es valido')
            return redirect(url_for('tu_cuenta'))
        elif password != r_password:
            flash('Los password no coinciden')
            return redirect(url_for('tu_cuenta'))
        else:  
            sql = 'INSERT INTO cliente (id, nombre, apellido, rut, telefono, direccion, correo, password, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values = (id, nombre, apellido, rut, telefono, direccion, correo, password, estado)
            cursor.execute(sql,values)
            midb.commit()
            
            flash('¡Te has registrado con exito!')
            return redirect(url_for('index'))

            # users = []
            # cursor.execute("SELECT * FROM cliente")
            # clientes = cursor.fetchall()

            # for c in clientes:
            #     users.append(User(id=c['id'], nombre=c['nombre'], apellido=c['apellido'], rut=c['rut'], telefono=c['telefono'], direccion=c['direccion'], correo=c['correo'], password=c['password']))        

            # cursor.execute("SELECT * FROM cliente WHERE correo = '%s'" %correo)
            # cliente  = cursor.fetchone()
            
            # user = [x for x in users if x.correo == correo][0]
            # session['user_id'] = user.id
            # session['tipo'] = 1

            # flash('¡Te has registrado con exito!')
            # return redirect(url_for('index'))

#---------- ACTUALIZAR CLIENTE -----------
@app.route('/actualizar_cliente/<int:id>', methods=['POST', 'GET'])
def actualizar_cliente(id):
    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rut = request.form['rut']
        telefono = int(request.form['telefono'])
        direccion = request.form['direccion']
        correo = request.form['correo']
        password = request.form['password']
        repetir_password = request.form['r_password']

        #validar rut
        # ------------------------------------------------
        i=0
        if rut.count('-') != 1 or rut.count('k') > 1:
            i = 2
        else:
            if len(rut) == 10:
                # -1 no existe || 
                if rut.find('k') == -1 or rut.find('k') == 9:
                    if rut.find('-') != 8:
                        i = 2
                else:
                    i = 2
            
            elif len(rut) == 9:
                if rut.find('k') == -1 or rut.find('k') == 8:
                    if rut.find('-') != 7:
                        i = 2
                else:
                    i = 2
            else:
                i = 2
        # ------------------------------------------------


        if password != repetir_password:
            flash('Los password no coinciden')
            return redirect(url_for('tu_cuenta'))

        elif i == 2:
            flash('El rut no es valido')
            return redirect(url_for('tu_cuenta'))

        elif password == repetir_password:
            cursor.execute(
                """
                UPDATE cliente
                SET nombre = %s,
                    apellido = %s,
                    rut = %s,
                    telefono = %s,
                    direccion = %s,
                    correo = %s,
                    password = %s
                WHERE id = %s
                """, (nombre, apellido, rut, telefono, direccion, correo, password, id)
            )
            midb.commit()
            flash('¡Tus datos han sido actualizados con exito!')
            return redirect(url_for('tu_cuenta'))

#---------- DISPARAR ALERTA PARA CERRAR SESION -----------
@app.route('/cerrar_sesion_cliente/<int:id>', methods=['POST', 'GET'])
def cerrar_sesion_cliente(id):
    flash('%s',id)
    return  redirect(url_for('tu_cuenta'))

#---------- CERRAR SESION DE FORMA DEFINITIVA -----------
@app.route('/destruir_sesion_cliente', methods=['POST', 'GET'])
def destruir_sesion_cliente():

    g.user = None
    session.pop('user_id', None)
    session.pop('tipo', None)
    return  redirect(url_for('tu_cuenta'))










#-------------------- ADMINISTRADOR ------------------
#-------------------- TU CUENTA ------------------
@app.route('/admin_cuenta',  methods=['POST', 'GET'])
def admin_cuenta():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2 and session['tipo'] != 3:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()

    cursor.execute("SELECT * FROM sucursal")
    sucursal = cursor.fetchall()

    suc = 0
    while suc < len(sucursal):
        if funcionario['id_sucursal'] == sucursal[suc]['id']:
            funcionario['nom_suc'] = sucursal[suc]['direccion']
            sucursal.remove(sucursal[suc])
        suc += 1

    return render_template('admin_tu_cuenta.html', funcionario=funcionario, sucursal=sucursal)

#---------- DISPARAR ALERTA PARA CERRAR SESION -----------
@app.route('/alerta_cerrar_sesion', methods=['POST', 'GET'])
def alerta_cerrar_sesion():
    flash("Cerrar sesion")
    return  redirect(url_for('admin_cuenta'))

#-------------------- ADMINISTRADOR ------------------
#---------- CERRAR SESION DE FORMA DEFINITIVA -----------
@app.route('/destruir_sesion_funcionario', methods=['POST', 'GET'])
def destruir_sesion_funcionario():
    
    g.user = None
    session.pop('user_id', None)
    session.pop('tipo', None)

    return  redirect(url_for('tu_cuenta'))

#------------- EL PROPIO FUNCIOANRIO ACTUALIZA SUS DATOS ---------------
@app.route('/actualiza_funcionario/<id>', methods=['POST'])
def funcionario_act(id):

    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2 and session['tipo'] != 3:
            return redirect(url_for('index'))

        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rut = request.form['rut']
        correo = request.form['correo']
        password = request.form['password']
        repetir_password = request.form['repetir_password']

        if request.form['rol'] == 'Cajero(a)':
            rol = 2
        elif request.form['rol'] == 'Repartidor':
            rol = 3
        else:
            rol = int(request.form['rol'])

        estado = int(request.form['estado'])

        if request.form['id_sucursal'] == 'Avenida Pedro Aguirre Cerda 9440':
            id_sucursal = 1
        elif request.form['id_sucursal'] == 'José Ignacio Zenteno 21':
            id_sucursal = 2
        elif request.form['id_sucursal'] == 'Avenida Angamos 236':
            id_sucursal = 3
        else:
            id_sucursal = int(request.form['id_sucursal'] )

        if password != repetir_password:
            flash('Los password no coinciden')
            return redirect(url_for('admin_cuenta'))

        elif password == repetir_password:
            cursor.execute(
            """
            UPDATE funcionario
            SET nombre = %s,
                apellido = %s,
                rut = %s,
                correo = %s,
                password = %s,
                rol = %s,
                estado = %s,
                id_sucursal = %s
            WHERE id = %s
            """, (nombre, apellido, rut, correo, password, rol, estado, id_sucursal, id)
            )
            midb.commit()
            flash('¡Tus datos fueron actualizados con exito!')
            return redirect(url_for('admin_cuenta'))    












#---------------- ADMINISTRADOR FUNCIONARAIO --------------------
#---------------- LAANZAR PAGINA DE LISTADO DE FUNCIONARIOS --------------------
@app.route('/admin_personal', methods=['POST', 'GET'])
def admin_personal():

    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if session['tipo'] != 2 and session['tipo'] != 3:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM funcionario")
    funcionarios = cursor.fetchall()
    cursor.execute("SELECT * FROM sucursal")
    sucursal = cursor.fetchall()
    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()


    return render_template('admin_personal.html', data=funcionarios, funcionario=funcionario, sucursal=sucursal)

#---------- REGISTRAR NUEVO FUNCIONARIO -----------
@app.route('/registrar_funcionario', methods=['POST', 'GET'])
def registrar_funcionario():
    if request.method == 'POST':
        cursor.execute('SELECT * FROM funcionario')
        funcionarios = cursor.fetchall()
        mayor = 0

        for funcionario in funcionarios:
            if mayor == 0:
                mayor = funcionario['id']
            else:
                mayor = funcionario['id'] if funcionario['id'] > mayor else mayor

        id = mayor + 1
        nombre = request.form.get('nombre', type=str).capitalize()
        apellido = request.form.get('apellido', type=str).capitalize()
        rut = request.form.get('rut', type=str).capitalize()
        correo = request.form.get('correo', type=str)
        password = request.form.get('password', type=str)
        r_password = request.form.get('r_password', type=str)
        rol = request.form.get('rol', type=int)
        estado = request.form.get('estado', type=int)
        id_sucursal = request.form.get('sucursal', type=int)

        if estado == 1:
            estado = True
        else:
            estado = False

        #validar rut
        i=0
        if rut.count('-') != 1 or rut.count('k') > 1:
            i = 2
        else:
            if len(rut) == 10:
                if rut.find('k') == -1 or rut.find('k') == 9:
                    if rut.find('-') != 8:
                        i = 2
                else:
                    i = 2
            
            elif len(rut) == 9:
                if rut.find('k') == -1 or rut.find('k') == 8:
                    if rut.find('-') != 7:
                        i = 2
                else:
                    i = 2
            else:
                i = 2
            
        for f in funcionarios:
            if f['rut'] ==  rut:
                i += 1 

        if i == 1:
            flash('Este funcionario ya existe')
            return redirect(url_for('admin_personal'))
        if i == 2:
            flash('El rut no es valido')
            return redirect(url_for('admin_personal'))
        elif password != r_password:
            flash('Los password no coinciden')
            return redirect(url_for('admin_personal'))
        else:  
            sql = 'INSERT INTO funcionario (id, nombre, apellido, rut, correo, password, rol, estado, id_sucursal) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values = (id, nombre, apellido, rut, correo, password, rol, estado, id_sucursal)
            cursor.execute(sql,values)
            midb.commit()
            flash('¡El funcionario se ha registrado con exito!')
            return redirect(url_for('admin_personal'))

#---------- FILTRAR FUNCIONARIO POR SU ESTADO (ACTIVADO/DESACTIIVADO) -----------
@app.route('/filtro_personal_estado', methods=['POST', 'GET'])
def filtrodinamico():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))    

    if request.method == 'POST':
        opcion = request.form.get('opcion', type=str)

        if opcion == 'todos':
            cursor.execute("SELECT * FROM funcionario")
            funcionarios = cursor.fetchall()
            return jsonify(funcionarios)
        else:    
            cursor.execute("SELECT * FROM funcionario WHERE estado = '%s'" %opcion)
            funcionarios = cursor.fetchall()
            return jsonify(funcionarios)

#---------- FILTRAR FUNCIONARIO POR SU SUCURSAL  -----------
@app.route('/filtro_personal_sucursal', methods=['POST', 'GET'])
def filtrodinamico_sucursal():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))    

    if request.method == 'POST':
        opcion = request.form.get('opcion', type=str)

        if opcion == 'todos':
            cursor.execute("SELECT * FROM funcionario")
            funcionarios = cursor.fetchall()
            return jsonify(funcionarios)

        else:    
            cursor.execute("SELECT * FROM funcionario WHERE id_sucursal = '%s'" %opcion)
            funcionarios = cursor.fetchall()
            return jsonify(funcionarios)

#------------- ENVIA INFORMACION DE FUNCIONARIO SELECCIONADO --------------- 
#--------------------- A PAGINA PARA ACTUALIZAR ------------------------------
@app.route('/modificar_func/<int:id>', methods=['POST', 'GET'])
def modificar_func(id):

    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if session['tipo'] != 2 and session['tipo'] != 3:
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM funcionario WHERE id = {0}'.format(id))
    data = cursor.fetchone()

    cursor.execute("SELECT * FROM rol_funcionario")
    rol = cursor.fetchall()

    r = 0
    while r < len(rol):
        if data['rol'] == rol[r]['id']:
            data['nom_rol'] = rol[r]['nombre']
            rol.remove(rol[r])
        r += 1


    cursor.execute("SELECT * FROM sucursal")
    sucursal = cursor.fetchall()

    suc = 0
    while suc < len(sucursal):
        if data['id_sucursal'] == sucursal[suc]['id']:
            data['nom_suc'] = sucursal[suc]['direccion']
            sucursal.remove(sucursal[suc])
        suc += 1
        

    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()

    return render_template('admin_modificar_funcionario.html', data=data, funcionario=funcionario, rol=rol, sucursal=sucursal)

#------------- ACTUALIZAR FUNCIONARIO ROL ADMINISTRADOR ---------------
@app.route('/actualizaF/<id>', methods=['POST'])
def actualiza_funcionario(id):
    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2 and session['tipo'] != 3:
            return redirect(url_for('index'))

        nombre = request.form['nombre']
        apellido = request.form['apellido']
        rut = request.form['rut']
        correo = request.form['correo']
        password = request.form['password']
        repetir_password = request.form['repetir_password']

        if request.form['rol'] == 'Cajero(a)':
            rol = 2
        elif request.form['rol'] == 'Repartidor':
            rol = 3
        else:
            rol = int(request.form['rol'])

        estado = int(request.form['estado'])
        id_sucursal = int(request.form['id_sucursal'])

        if password != repetir_password:
            flash('Los password no coinciden')
            return redirect(url_for('modificar_func', id=id))

        elif password == repetir_password:
            cursor.execute(
            """
            UPDATE funcionario
            SET nombre = %s,
                apellido = %s,
                rut = %s,
                correo = %s,
                password = %s,
                rol = %s,
                estado = %s,
                id_sucursal = %s
            WHERE id = %s
            """, (nombre, apellido, rut, correo, password, rol, estado, id_sucursal, id)
            )
            midb.commit()
            flash('¡Funcionario actualizado con exito!')
            return redirect(url_for('admin_personal'))












#---------------- ADMINISTRADOR TIENDA--------------------
#----------------- LISTA DE PRODUCTOS ---------------
@app.route('/admin_tienda',  methods=['POST', 'GET'])
def admin_tienda():

    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM producto")
    productos = cursor.fetchall()
    cursor.execute("SELECT * FROM categoria")
    categorias = cursor.fetchall()


    cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'] )
    funcionario = cursor.fetchone()
    return render_template('admin_tienda.html', data=productos, funcionario=funcionario, categorias=categorias)

#----------------- AGREGAR NUEVO PRODUCTO ---------------
@app.route('/agregar_producto',  methods=['POST', 'GET'])
def agregar_producto():
 if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2:
            return redirect(url_for('index'))

        cursor.execute('SELECT * FROM producto')
        productos = cursor.fetchall()
        mayor = 0

        for producto in productos:
            if mayor == 0:
                mayor = producto['id']
            else:
                mayor = producto['id'] if producto['id'] > mayor else mayor

        id = mayor + 1
        sku = request.form.get('sku', type=str).upper()
        nombre = request.form.get('nombre', type=str).capitalize()
        precio = request.form.get('precio', type=int)
        cant_tienda = request.form.get('cant_tienda', type=int)
        stock_critico = request.form.get('stock_critico', type=int)
        cant_bodega = request.form.get('cant_bodega', type=int)
        descripcion = request.form.get('descripcion', type=str).capitalize()
        categoria = request.form.get('categoria', type=int)
        estado = True

        file = request.files['imagen']
        nombre_imagen = secure_filename(file.filename)

        # validar SKU
        i = 0
        for p in productos:
            if p['sku'] == sku:
                i += 1

        if i == 1:
            flash('El SKU ya existe')
            return redirect(url_for('admin_tienda'))
        else:
            sql = 'INSERT INTO producto (id, sku, nombre, precio, cant_tienda, stock_critico, cantidad_bodega, descripcion, imagen, categoria, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values = (id, sku, nombre, precio, cant_tienda, stock_critico, cant_bodega, descripcion, nombre_imagen, categoria, estado)
            cursor.execute(sql, values)
            midb.commit()

            file.save(os.path.join(app.config['cargar_imagen'], nombre_imagen))

            # NUEVO REGISTRO EN AUDITORIA PRODUCTO
            #------------------------------------------
            cursor.execute('SELECT * FROM auditoria_productos')
            auditoria_productos = cursor.fetchall()
            contador_ap = 0

            for prod in auditoria_productos:
                if contador_ap == 0:
                    contador_ap = prod['id']
                else:
                    contador_ap = prod['id'] if prod['id'] > contador_ap else contador_ap


            # Definir FECHA ACTUAL
            fecha_ = date.today().strftime('%Y-%m-%d')
            anio = fecha_[0:4]
            mes = fecha_[5:7]
            dia = fecha_[8:11]

            id_audi = contador_ap + 1
            hora = time.strftime("%H:%M")
            fecha = date(int(anio), int(mes), int(dia))
            id_funcionario = session['user_id']
            id_producto = id
            cant_tienda_an = cant_tienda
            cant_tienda_ac = cant_tienda
    
            sql = """
            INSERT INTO auditoria_productos 
            (id, hora, fecha, id_funcionario, id_producto, cant_tienda_an, cant_tienda_ac) 
            VALUES 
            (%s,%s,%s,%s,%s,%s,%s)
            """
            values = (id_audi, hora, fecha, id_funcionario, id_producto, cant_tienda_an, cant_tienda_ac) 

            cursor.execute(sql, values)
            midb.commit()

            #------------------------------------------


            flash('¡Producto agregado con exito!')
            return redirect(url_for('admin_tienda'))

#----------------- AGREGAR NUEVA CATEGORIA ---------------
@app.route('/agregar_categoria',  methods=['POST', 'GET'])
def agregar_categoria():
    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2:
            return redirect(url_for('index'))

        cursor.execute('SELECT * FROM categoria')
        categorias = cursor.fetchall()
        mayor = 0

        for cat in categorias:
            if mayor == 0:
                mayor = cat['id']
            else:
                mayor = cat['id'] if cat['id'] > mayor else mayor

        id = mayor + 1
        nombre = request.form.get('nombre', type=str).capitalize()

        # VALIDAR NOMBRE CATEGORIA
        i = 0
        for c in categorias:
            if c['nombre'] == nombre:
                i += 1
        
        if i == 1:
            flash('La categoria ya existe')
            return redirect(url_for('admin_tienda'))
        else:
            sql = 'INSERT INTO categoria (id, nombre) VALUES (%s, %s)'
            values = (id, nombre)
            cursor.execute(sql, values)
            midb.commit()

            flash('¡Categoria agregada con exito!')
            return redirect(url_for('admin_tienda'))

#----------------- CAMBIAR ESTADO CATEGORIA (ACTIVADO-DESACTIVADO) ---------------
@app.route('/estado_categoria',  methods=['POST', 'GET'])
def estado_categoria():
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2:
            return redirect(url_for('index'))
    
        categoria = request.form.get('categoria', type=int)
        cursor.execute("SELECT * FROM categoria WHERE id = '%s'" %categoria)
        cat = cursor.fetchone()

        if cat['estado'] == 1:
            estado = 0
        else:
            estado = 1

        cursor.execute(
            """
            UPDATE categoria
            SET estado = %s
            WHERE id = %s
            """, (estado, categoria)
        )
        midb.commit()
        

        flash('¡Categoria actualizada con exito!')
        return redirect(url_for('admin_tienda'))

#------------- ENVIA INFORMACION DEL PRODUCTO SELECCIONADO --------------- 
#--------------------- A PAGINA PARA ACTUALIZAR ------------------------------
@app.route('/modificar_prod/<int:id>', methods=['POST', 'GET'])
def modificar_producto(id):

    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))


    cursor.execute('SELECT * FROM producto WHERE id = {0}'.format(id))
    producto = cursor.fetchone()
    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()
    cursor.execute('SELECT * FROM categoria')
    categorias = cursor.fetchall()

    for cat in categorias:
        if cat['id'] == producto['categoria']:
            producto['nom_cat'] = cat['nombre']
            categorias.remove(cat)


    return render_template('admin_modificar_producto.html', data=producto, funcionario=funcionario, categorias=categorias)
#------------- MODIFICAR PRODUCTO ---------------
@app.route('/actualizaP/<int:id>', methods=['POST'])
def actualizar_prod(id):
 if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2:
            return redirect(url_for('index'))

        cursor.execute("SELECT * FROM producto WHERE id = {0}".format(id))
        producto = cursor.fetchone()
        
        cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'])
        funcionario = cursor.fetchone()

        id_producto = producto['id']
        cantidad_tienda_anterior = producto['cant_tienda']
        
        sku = request.form['sku']
        nombre = request.form['nombre']
        precio = int(request.form['precio'])
        cant_tienda = int(request.form['cant_tienda'])
        stock_critico = int(request.form['stock_critico'])
        cant_bodega = int(request.form['cant_bodega'])
        descripcion = request.form['descripcion']
        categoria = int(request.form['categoria'])
        estado = request.form['estado']

        file = request.files['imagen']

        if file == '':
            nombre_imagen = producto['imagen']
        else:
            nombre_imagen = secure_filename(file.filename)

        file.save(os.path.join(app.config['cargar_imagen'], nombre_imagen))

        cursor.execute(
        """
        UPDATE producto
        SET sku = %s,
            nombre = %s,
            precio = %s,
            cant_tienda = %s,
            stock_critico = %s,
            cantidad_bodega = %s,
            descripcion = %s,
            imagen = %s,
            categoria = %s,
            estado = %s
        WHERE id = %s
        """, (sku, nombre, precio, cant_tienda, stock_critico, cant_bodega, descripcion, nombre_imagen, categoria, estado, id)
        )
        # ACTUALIZA EL PRODUCTO EN LA BD
        midb.commit()
      


        # REALIZA EL INSERT EN LA TABLA AUDITORIA_PRODUCTOS
        if funcionario['rol'] == 2:

            cursor.execute('SELECT * FROM auditoria_productos')
            auditoria_productos = cursor.fetchall()

            # Definir ID
            mayor = 0
            for producto in auditoria_productos:
                if mayor == 0:
                    mayor = producto['id']
                else:
                    mayor = producto['id'] if producto['id'] > mayor else mayor        


            # Definir FECHA ACTUAL
            fecha_ = date.today().strftime('%Y-%m-%d')
            anio = fecha_[0:4]
            mes = fecha_[5:7]
            dia = fecha_[8:11]

            # DEFINIR VARIABLES PARA LA TABLA AUDITORIA_PRODUCTOS
            id_auditoria = mayor + 1
            hora = time.strftime("%H:%M")
            fecha = date(int(anio), int(mes), int(dia))
            id_funcionario = session['user_id']
            id_producto = id
            cant_tienda_an = cantidad_tienda_anterior
            cant_tienda_ac = cant_tienda

            sql = """
            INSERT INTO auditoria_productos 
            (id, hora, fecha, id_funcionario, id_producto, cant_tienda_an, cant_tienda_ac) 
            VALUES 
            (%s,%s,%s,%s,%s,%s,%s)
            """
            values = (id_auditoria, hora, fecha, id_funcionario, id_producto, cant_tienda_an, cant_tienda_ac) 

            cursor.execute(sql, values)
            midb.commit()

            flash('¡Producto actualizado con exito!')
            return redirect(url_for('admin_tienda'))

        else:
            flash('¡Producto actualizado con exito!')
            return redirect(url_for('admin_tienda'))



















#---------------- ADMINISTRADOR STOCK CRITICO--------------------
#-------- LISTA DE PRODUCTOS MAS CERCANOS AL STOCK CRITICO ---------------
@app.route('/admin_stock',  methods=['POST', 'GET'])
def admin_stock():

    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'] )
    funcionario = cursor.fetchone()

    diferencia_dic = []

    cursor.execute("SELECT * FROM producto")
    productos = cursor.fetchall()

    diferencia_dic = []
    for producto in productos:
        diferencia = producto['cant_tienda'] - producto['stock_critico']

        diferencia_dic.append({
            'producto': producto['nombre'],
            'cantidad_tienda': producto['cant_tienda'],
            'stock_critico': producto['stock_critico'],
            'diferencia': diferencia
        })
        
    stock = sorted( diferencia_dic, key=lambda prod: prod['diferencia'] )

    return render_template('admin_stock.html', stock=stock, funcionario=funcionario)


#-------- LISTA DE PRODUCTOS MAS CERCANOS AL STOCK CRITICO POR SUCURSAL ---------------
# --------------------- SOLO LO PUEDE HACER EL ADMINISTRADOR--------------------------
@app.route('/stock_sucursal',  methods=['POST', 'GET'])
def stock_sucursal():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))

    if request.method == 'POST':

        cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'] )
        funcionario = cursor.fetchone()

        id_sucursal = request.form['sucursal']
        cursor.execute("SELECT * FROM producto_sucursal WHERE id_sucursal = '%s'" %id_sucursal)
        producto_sucursal = cursor.fetchall()

        diferencia_dic = []
        for pro in producto_sucursal:
            diferencia = pro['cant_tienda'] - pro['stock_critico']

            cursor.execute("SELECT * FROM producto WHERE id = '%s'" %pro['id_producto'])
            prod = cursor.fetchone()

            cursor.execute("SELECT * FROM sucursal WHERE id = '%s'" %id_sucursal)
            sucursal = cursor.fetchone()

            diferencia_dic.append({
                'producto': prod['nombre'],
                'sucursal': sucursal['direccion'],
                'cantidad_tienda': pro['cant_tienda'],
                'stock_critico': pro['stock_critico'],
                'diferencia': diferencia
            })

        stock = sorted( diferencia_dic, key=lambda prod: prod['diferencia'] )
        
        cursor.execute("SELECT * FROM sucursal WHERE estado = 1")
        sucursales = cursor.fetchall()

        return render_template('admin_stock.html', stock=stock, funcionario=funcionario, sucursales=sucursales)














#---------------- ADMINISTRADOR PEDIDOS --------------------
#------------------- PAGINA PEDIDOS --------------
@app.route('/admin_pedidos', methods=['POST', 'GET'])
def admin_pedidos():

    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if session['tipo'] != 2:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()
    
    hoy = datetime.now().date()


    # ROL = 1   ==> 'ADMINISTRADOR' 
    if funcionario['rol'] == 1:
        cursor.execute("SELECT * FROM pedido WHERE fecha = '%s' " %hoy)
        pedidos = cursor.fetchall()
        
        nombre_cliente = []
        apellido_cliente = []
        z = 0

        while z < len(pedidos):
            cursor.execute("SELECT * FROM cliente WHERE id = '%s'" %pedidos[z]['id_cliente'] )
            cliente = cursor.fetchone()
            nombre_cliente.append(cliente['nombre'])
            apellido_cliente.append(cliente['apellido'])
            z += 1

        y = 0
        while y < len(nombre_cliente):
            pedidos[y]['nombre_cliente'] = nombre_cliente[y] + ' ' + apellido_cliente[y]
            y += 1

        a = reversed(pedidos)

        if pedidos != None:
            p = 0
            for ped in pedidos:
                if ped['estado'] == 3:
                    p = 1

            if p == 1:
                cursor.execute("SELECT * FROM funcionario WHERE rol = 3")
                rep = cursor.fetchall()
            else:
                rep = None
        else:
            rep = None

        return render_template('admin_pedidos.html', data=a, funcionario=funcionario, repartidores=rep, fecha=hoy)

    # ROL = 3   ==> 'REPARTIDOR'
    elif funcionario['rol'] == 3:
        cursor.execute('SELECT * FROM pedido WHERE id_repartidor = {0}'.format(funcionario['id'] )) 
        pedidos = cursor.fetchall()

        nombre_cliente = []
        apellido_cliente = []
        z = 0

        while z < len(pedidos):
            cursor.execute("SELECT * FROM cliente WHERE id = '%s'" %pedidos[z]['id_cliente'] )
            cliente = cursor.fetchone()
            nombre_cliente.append(cliente['nombre'])
            apellido_cliente.append(cliente['apellido'])
            z += 1

        y = 0
        while y < len(nombre_cliente):
            pedidos[y]['nombre_cliente'] = nombre_cliente[y] + ' ' + apellido_cliente[y]
            y += 1

        a = reversed(pedidos)

        return render_template('admin_pedidos.html', data=a, funcionario = funcionario, fecha=hoy)        

    # ROL = 2   ==> 'CAJERO'
    else:
        cursor.execute("SELECT * FROM pedido WHERE id_sucursal = '%s' AND fecha = '%s' " %(funcionario['id_sucursal'], hoy))        
        pedidos = cursor.fetchall()

        nombre_cliente = []
        apellido_cliente = []
        z = 0

        while z < len(pedidos):
            cursor.execute("SELECT * FROM cliente WHERE id = '%s'" %pedidos[z]['id_cliente'] )
            cliente = cursor.fetchone()
            nombre_cliente.append(cliente['nombre'])
            apellido_cliente.append(cliente['apellido'])
            z += 1

        y = 0
        while y < len(nombre_cliente):
            pedidos[y]['nombre_cliente'] = nombre_cliente[y] + ' ' + apellido_cliente[y]
            y += 1

        a = reversed(pedidos)

        return render_template('admin_pedidos.html', data=a, funcionario = funcionario, fecha=hoy)

#------------------- FILTRAR PEDIDOS POR FECHA--------------
@app.route('/filtrar_pedido', methods=['POST', 'GET'])
def filtrar_pedido():

    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2:
            return redirect(url_for('index'))

    hoy = request.form['hoy']

    cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'])
    funcionario = cursor.fetchone()    

    # ROL = 1   ==> 'ADMINISTRADOR' 
    if funcionario['rol'] == 1:
        cursor.execute("SELECT * FROM pedido WHERE fecha = '%s' " %hoy)
        pedidos = cursor.fetchall()

    # ROL = 2   ==> 'CAJERO'
    elif funcionario['rol'] == 2: 
        cursor.execute("SELECT * FROM pedido WHERE id_sucursal = '%s' AND fecha = '%s' " %(funcionario['id_sucursal'], hoy))    
        pedidos = cursor.fetchall()

    # ROL = 3   ==> 'REPARTIDOR'
    else:
        cursor.execute("SELECT * FROM pedido WHERE id_repartidor = '%s' AND fecha = '%s'" %(funcionario['id'], hoy)  ) 
        pedidos = cursor.fetchall()

    a = reversed(pedidos)
    
    return render_template('admin_pedidos.html', data=a, funcionario = funcionario, fecha= hoy)

#----------- DISPARA ALERTA PARA CAMBIAR ESTADO DEL PEDIDO --------------
@app.route('/act_estado/<int:id>', methods=['POST', 'GET'])
def act_estado(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if session['tipo'] != 2:
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM pedido WHERE id = {0}".format(id))
    pedido = cursor.fetchone()
    if pedido['estado'] == 1:
        flash(['1', 'Ingresado', '2','En proceso', '5', 'Cancelado', id] )
    elif pedido['estado'] == 2:
        flash(['2', 'En proceso', '3','Enviado', '5', 'Cancelado', id ] )
    
    return redirect(url_for('admin_pedidos'))

#----------- DISPARA ALERTA PARA CAMBIAR ESTADO DEL PEDIDO (REPARTIDOR)--------------
@app.route('/act_estado_repartidor/<int:id>', methods=['POST', 'GET'])
def actualizar_estado_repartidor(id):
    
    flash([ '4', 'Entregado', '5', 'Cancelado', id])
    return redirect(url_for('admin_pedidos'))

#----------- ACTUALIZAR ESTADO DEL PEDIDO --------------
@app.route('/modificar_estado/<int:id>', methods=['POST', 'GET'])
def modificar_estado(id):
    if request.method == 'POST':
        
        if 'user_id' not in session:
            return redirect(url_for('index'))    

        if session['tipo'] != 2:
            return redirect(url_for('index'))

        estado = int(request.form['estado'])
        cursor.execute(
            """
            UPDATE pedido
            SET estado = %s
            WHERE id = %s
            """, (estado, id)
        )
        midb.commit()

        if estado == 3:
            cursor.execute("SELECT * FROM funcionario WHERE rol = 3")
            repartidores = cursor.fetchall()

            if repartidores != None:
                return render_template('admin_pedidos.html', repartidores=repartidores)
            else:
                return render_template('admin_pedidos.html', repartidores=None)
        else:
            return render_template('admin_pedidos.html', repartidores=None)

#----------- INFORMACION DEL PEDIDO (PRODUCTOS, CLIENTE, FUNCIONARIO) --------------
@app.route('/informacion_pedido/<int:id>', methods=['POST', 'GET'])
def informacion_pedido(id):

    if 'user_id' not in session:
        return redirect(url_for('index'))    

    if session['tipo'] != 2:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()


    cursor.execute("SELECT * FROM pedido_producto WHERE id_pedido = '%s'" %id)
    pedido_producto = cursor.fetchall()

    productos = []

    for pp in pedido_producto:
        cursor.execute("SELECT * FROM producto WHERE id = '%s'" %pp['id_producto'])
        producto = cursor.fetchone()
        productos.append({ 'nombre':producto['nombre'], 'cantidad':pp['cantidad'] })

    cursor.execute("SELECT * FROM pedido WHERE id = '%s'" %id)
    pedido = cursor.fetchone()
    cursor.execute("SELECT * FROM cliente WHERE id = '%s'" %pedido['id_cliente'])
    cliente = cursor.fetchone()

    cursor.execute("SELECT * FROM funcionario WHERE rol = 3")
    repartidores = cursor.fetchall()

    if pedido['id_repartidor'] != None:
        for nombre_rep in repartidores:
            if pedido['id_repartidor'] == nombre_rep['id']:
                pedido['nombre_rep'] = nombre_rep['nombre'] + ' ' + nombre_rep['apellido']

    return render_template("admin_detalle_pedido.html", funcionario=funcionario, productos=productos, cliente=cliente, repartidores=repartidores, pedido=pedido)

#----------- ASIGNAR REPARTIDOR AL PEDIDO --------------
@app.route('/asignar_repartidor', methods= ['POST', 'GET'] )
def asignar_repatidor():
    if request.method == 'POST':
        
        repartidor = int(request.form['repartidor'])
        pedido = request.form['pedido']

        cursor.execute("SELECT * FROM funcionario WHERE rol = 3")
        repartidores = cursor.fetchall()

        # Repartidor en su posicion X es el que se esta enviando
        x = repartidor - 1
        
        id_repartidor = repartidores[x]['id']

        cursor.execute(
            """
            UPDATE pedido
            SET id_repartidor = %s
            WHERE id = %s
            """, (id_repartidor,pedido)
        )
        midb.commit()

        flash("Repartidor asignado con exito")
        return redirect(url_for('admin_pedidos'))















#---------------- ------ADMINISTRADOR REPORTES --------------------
#----------------------- VISTA PAGINA REPORTES  ---------------
@app.route('/admin_reportes',  methods=['POST', 'GET'])
def admin_reportes():

    if 'user_id' not in session:
        return redirect(url_for('index'))

    if session['tipo'] != 2:
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM producto')
    producto = cursor.fetchall()
        
    contador_p = 0
    nombre = []
    cantidad = []
    valor = []
    ganancia = []
    while contador_p < len(producto):
        nombre.append(producto[contador_p]['nombre'] )
        cantidad.append(0)
        valor.append(producto[contador_p]['precio'])
        ganancia.append(0)
        contador_p += 1

    z = 0
    tabla = []
    while z < len(nombre):
        tabla.append( {'nombre': nombre[z], 'cantidad': cantidad[z],'valor': valor[z], 'ganancia': ganancia[z] } )
        z += 1
    
    tabla_reporte_prod.append(tabla)

    cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'])
    funcionario = cursor.fetchone()
    
    # hasta = datetime.now().date()

    return render_template('admin_reporte_pedidos.html', tabla=tabla, total=0, funcionario=funcionario, auditoria=None)

#----------------------- FILTRAR REPORTE DE VENTA DE PRODUCTOS  ---------------
@app.route('/filtrar_reportes',  methods=['POST', 'GET'])
def filtrar_reportes():
    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2:
            return redirect(url_for('index'))

        cursor.execute('SELECT * FROM pedido')
        pedidos = cursor.fetchall()

        desde = request.form['desde']
        hasta = request.form['hasta']

        if hasta == '':
            hasta = datetime.now().date()

        #-------------- PEDIDOS PRODUCTO ----------------------- 
        lista_fecha_pedidos = []
        lista_id_pedidos = []

        for p in pedidos:
            lista_fecha_pedidos.append(p['fecha'])
            lista_id_pedidos.append(p['id'])


        # ---------------------- FILTRAR FECHAS DE PEDIDOS ------------------------------------
        df = pd.DataFrame({'Fechainicio':pd.to_datetime(lista_fecha_pedidos), 'ident':lista_id_pedidos})
        df = df.set_index(["Fechainicio"])
        filtro_pedido = df.loc[desde:str(hasta)]

        z = 0
        pedidos_filtrados = []

        while z < len(filtro_pedido.index):  # NUMERO DE FECHAS ENCONTRADAS DENTRO DEL RANGO   
            id = int(filtro_pedido.values[z])  # ID DE CADA PEDIDO
            cursor.execute("SELECT * FROM pedido_producto WHERE id_pedido = '%s'" %id)
            pediprod = cursor.fetchall()
            
            for pepr in pediprod:
                pedidos_filtrados.append(pepr)    
            z += 1

        cursor.execute('SELECT * FROM producto')
        producto = cursor.fetchall()

        maximo = (max(producto, key=lambda d: d['id']))
        id_maximo_prod = (f"{maximo['id']}")

        id_prod = 1
        tabla_suma = []
        tabla_ordenada = []

        while id_prod <= int(id_maximo_prod):
            for asd in pedidos_filtrados:
                if asd['id_producto'] == id_prod:
                    tabla_suma.append(asd)
            if tabla_suma != []:
                v = 0
                for tbs in tabla_suma:
                    v = v + int(tbs['cantidad'])
                    idpro = tbs['id_producto']
                tabla_suma = []
                dic = {"id_producto": idpro, "cantidad": v}
                tabla_ordenada.append(dic)
            id_prod += 1


        #--------------- CARGAR LOS NOMBRES -------------------------
        #--------------- CARGAR LA CANTIDAD VENDIDA -------------------------
        nombre = []
        cantidad = []
        valor = []
        ganancia = []
        q = 0
        contador_p = 0
        gan = 0

        while contador_p < len(producto):
            nombre.append(producto[contador_p]['nombre'])
            valor.append(producto[contador_p]['precio'])
            for tabla_or in tabla_ordenada:
                if tabla_or['id_producto'] == producto[contador_p]['id']:
                    q = 1
                    cantidad.append(int(tabla_or['cantidad'] ))
                    gan = int(producto[contador_p]['precio']) * int(tabla_or['cantidad'])
                    ganancia.append(gan)
                    break
            if q == 0:        
                cantidad.append(int(0))
                ganancia.append(int(0))
            contador_p += 1
            q = 0
            gan = 0


        total = sum(ganancia)
        z = 0
        tabla = []
        while z < len(nombre):
            tabla.append( {'nombre': nombre[z], 'cantidad': cantidad[z], 'valor': valor[z], 'ganancia': ganancia[z]  } )
            z += 1

        cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'])
        funcionario = cursor.fetchone()
        
        tabla_reporte_prod.append(tabla)
        
        # ----------------------- FILTRAR AUDITORIA --------------------------------------
        cursor.execute('SELECT * FROM auditoria_productos')
        auditoria_productos = cursor.fetchall()

        lista_fecha_audpro = []
        lista_id_audpro = []

        for ap in auditoria_productos:
            lista_fecha_audpro.append(ap['fecha'])
            lista_id_audpro.append(ap['id'])

        df = pd.DataFrame({'Fechainicio':pd.to_datetime(lista_fecha_audpro), 'ident':lista_id_audpro})
        df = df.set_index(["Fechainicio"])
        filtro_audpro = df.loc[desde:str(hasta)]

        z = 0
        audpro_filtrados = []
        nombre_funcionario = []
        apellido_funcionario = []
        nombre_producto = []

        while z < len(filtro_audpro.index):  # NUMERO DE FECHAS ENCONTRADAS DENTRO DEL RANGO   
            id = int(filtro_audpro.values[z])  # ID DE CADA audpro
            cursor.execute("SELECT * FROM auditoria_productos WHERE id = '%s'" %id)
            audpro = cursor.fetchone()
            audpro_filtrados.append(audpro)

            cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %audpro['id_funcionario'])
            funci = cursor.fetchone()
            nombre_funcionario.append(funci['nombre'])
            apellido_funcionario.append(funci['apellido'])

            cursor.execute("SELECT * FROM producto WHERE id = '%s'" %audpro['id_producto'])
            prod = cursor.fetchone()
            nombre_producto.append(prod['nombre'])
            z += 1


        q = 0
        tabla_auditoria = []
        while q < len(audpro_filtrados):
            tabla_auditoria.append(
                {
                    'hora': audpro_filtrados[q]['hora'],
                    'fecha': audpro_filtrados[q]['fecha'],
                    'nombre_funcionario': nombre_funcionario[q] + ' ' + apellido_funcionario[q],
                    'nombre_producto': nombre_producto[q],
                    'cant_tienda_an': audpro_filtrados[q]['cant_tienda_an'],
                    'cant_tienda_ac': audpro_filtrados[q]['cant_tienda_ac'],
                }
            )
            q += 1

        # ------------------------ FIN AUDITORIA -----------------------------------------

        a = reversed(tabla_auditoria)
        tabla_reporte_aud.append(tabla_auditoria)

        return render_template('admin_reporte_pedidos.html', total = total, tabla=tabla, funcionario=funcionario, auditoria=a, desde=desde, hasta=hasta)

    else:
        cursor.execute('SELECT * FROM producto')
        producto = cursor.fetchall()

        contador_p = 0
        nombre = []
        cantidad = []
        valor = []
        ganancia = []
        while contador_p < len(producto):
            nombre.append(producto[contador_p]['nombre'])
            valor.append(producto[contador_p]['precio'])
            cantidad.append(0)
            ganancia.append(0)
            contador_p += 1

        z = 0
        tabla = []
        while z < len(nombre):
            tabla.append( {'nombre': nombre[z], 'cantidad': cantidad[z], 'valor': valor[z],  'ganancia': ganancia[z] } )
            z += 1


        cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %session['user_id'])
        funcionario = cursor.fetchone()

        tabla_reporte_prod.append(tabla)
        return render_template('admin_reporte_pedidos.html', total=0, tabla=tabla, funcionario=funcionario, auditoria=None)


#----------------------- GENERAR REPORTE DE PRODUCTO VENDIDOS --------------- 
@app.route("/informe_pdf_ventas/<desde>/<hasta>", methods=['POST', 'GET'])
def reporte_pdf(desde, hasta):

    cantidad_reporte = len(tabla_reporte_prod)
    cant = cantidad_reporte - 1
    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # TEXTO
    pdf.set_font('Arial', 'B', 15)

    # TITULO
    pdf.cell(w=0, h=15, txt='Venta por productos', border=1, ln=1, align='C', fill=0)

    pdf.cell(w=0, h=15, txt='Rango de fechas ' + desde + ' / ' + hasta, border=1, ln=1, align='C', fill=0)

    pdf.ln(5)

    # ENCABEZADO
    pdf.cell(w=80, h=15, txt='Nombre', border=1, align='C', fill=0)
    pdf.cell(w=20, h=15, txt='Ventas', border=1, align='C', fill=0)
    pdf.cell(w=50, h=15, txt='Valor unidad', border=1, align='C', fill=0)
    pdf.multi_cell(w=0, h=15, txt='Ganancia', border=1, align='C', fill=0)

    pdf.set_font('Arial', '', 15)

    # VALORES
    for prod in tabla_reporte_prod[cant]:
        pdf.cell(w=80, h=12, txt=str(prod['nombre']), border=1, align='C', fill=0)
        pdf.cell(w=20, h=12, txt=str(prod['cantidad']), border=1, align='C', fill=0)
        pdf.cell(w=50, h=12, txt=str(prod['valor']), border=1, align='C', fill=0)
        pdf.multi_cell(w=0, h=12, txt=str(prod['ganancia']), border=1, align='C', fill=0)
    
    total = 0

    for prod in tabla_reporte_prod[cant]:
        if total == 0:
            total = prod['ganancia']
        else:
            total = total + prod['ganancia']
    
    pdf.ln(10)

    # TOTAL GANADO
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(w=150, h=12, txt='Total vendido', border=1, align='C', fill=0)
    pdf.set_font('Arial', '', 15)
    pdf.cell(w=0, h=12, txt=str(total), border=1, align='C', fill=0)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=Venta de productos.pdf'})

#----------------------- GENERAR REPORTE DE AUDITORIA  --------------- 
@app.route('/informe_pdf_auditoria/<desde>/<hasta>', methods=['POST', 'GET'])
def reporte_pdf_auditoria(desde, hasta):
    
    aud_pro = len(tabla_reporte_aud)
    cant = aud_pro - 1

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # TEXTO
    pdf.set_font('Arial', 'B', 15)
    
    # TITULO
    pdf.cell(w=0, h=15, txt='Auditoria por productos', border=1, ln=1, align='C', fill=0)
    pdf.cell(w=0, h=15, txt='Rango de fechas ' + desde + ' / ' + hasta, border=1, ln=1, align='C', fill=0)

    pdf.ln(5)

    pdf.cell(w=0, h=15, txt='An = Anterior / Ac = Actual', border=1, ln=1, align='C', fill=0)


    for prod in tabla_reporte_aud[cant]:

        # TEXTO ENCABEZADO
        pdf.set_font('Arial', 'B', 15)

        # ENCABEZADO
        pdf.cell(w=25, h=15, txt='Hora', border=1, align='C', fill=0)
        pdf.cell(w=35, h=15, txt='Fecha', border=1, align='C', fill=0)
        pdf.cell(w=50, h=15, txt='Funcionario', border=1, align='C', fill=0)
        pdf.multi_cell(w=0, h=15, txt='Producto', border=1, align='C', fill=0)
  

        # TEXTO VALORES
        pdf.set_font('Arial', '', 15)
        
        # VALORES
        pdf.cell(w=25, h=12, txt=str(prod['hora']), border=1, align='C', fill=0)
        pdf.cell(w=35, h=12, txt=str(prod['fecha']), border=1, align='C', fill=0)
        pdf.cell(w=50, h=12, txt=str(prod['nombre_funcionario']), border=1, align='C', fill=0)
        pdf.multi_cell(w=0, h=12, txt=str(prod['nombre_producto']), border=1, align='C', fill=0)

        # TEXTO ENCABEZADO
        pdf.set_font('Arial', 'B', 15)

        pdf.multi_cell(w=60, h=15, txt='Stock An / Stock Ac', border=1, align='C', fill=0)

        # TEXTO VALORES
        pdf.set_font('Arial', '', 15)

        # VALORES
        pdf.multi_cell(w=60, h=12, txt=str(prod['cant_tienda_an']) + ' / ' + str(prod['cant_tienda_ac']), border=1, align='C', fill=0)


        pdf.ln(10)


    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename=auditoria_productos.pdf'})


    









#---------------- ------ADMINISTRADOR SUCURSAL --------------------
#----------------------- VISTA PAGINA SUCURSAL  ---------------
@app.route('/admin_sucursal', methods=['POST', 'GET'])
def admin_sucursal():

    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if session['tipo'] != 2 and session['tipo'] != 3:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM sucursal")
    sucursales = cursor.fetchall()
    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()


    return render_template('admin_sucursal.html', funcionario=funcionario, sucursales=sucursales)

#---------- REGISTRAR NUEVA SUCURSAL -----------
@app.route('/registrar_sucursal', methods=['POST', 'GET'])
def registrar_sucursal():
    if request.method == 'POST':
        cursor.execute('SELECT * FROM sucursal')
        sucursales = cursor.fetchall()
        mayor = 0

        for sucursal in sucursales:
            if mayor == 0:
                mayor = sucursal['id']
            else:
                mayor = sucursal['id'] if sucursal['id'] > mayor else mayor

        id = mayor + 1
        razon_social = request.form.get('razon_social', type=str).capitalize()
        giro = request.form.get('giro', type=str).capitalize()
        nombre = request.form.get('nombre', type=str).capitalize()
        rut = request.form.get('rut', type=str)
        telefono = request.form.get('telefono', type=int)
        direccion = request.form.get('direccion', type=str)
        correo = request.form.get('correo', type=str)
        estado = request.form.get('estado', type=int)


        if estado == 1:
            estado = True
        else:
            estado = False

        #validar rut
        i=0
        if rut.count('-') != 1 or rut.count('k') > 1:
            i = 2
        else:
            if len(rut) == 10:
                if rut.find('k') == -1 or rut.find('k') == 9:
                    if rut.find('-') != 8:
                        i = 2
                else:
                    i = 2
            
            elif len(rut) == 9:
                if rut.find('k') == -1 or rut.find('k') == 8:
                    if rut.find('-') != 7:
                        i = 2
                else:
                    i = 2
            else:
                i = 2

        if i == 2:
            flash('El rut no es valido')
            return redirect(url_for('admin_sucursal'))
        else:  
            sql = 'INSERT INTO sucursal (id, razon_social, giro, nombre, rut, telefono, direccion, correo, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values = (id, razon_social, giro, nombre, rut, telefono, direccion, correo, estado)
            cursor.execute(sql,values)
            midb.commit()
            flash('¡La sucursal se ha registrado con exito!')
            return redirect(url_for('admin_sucursal'))

#------------- ENVIA INFORMACION DE SUCURSAL SELECCIONADA --------------- 
#--------------------- A PAGINA PARA ACTUALIZAR ------------------------------
@app.route('/modificar_suc/<int:id>', methods=['POST', 'GET'])
def modificar_suc(id):

    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if session['tipo'] != 2 and session['tipo'] != 3:
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM sucursal WHERE id = {0}'.format(id))
    sucursal = cursor.fetchone()

    cursor.execute("SELECT * FROM funcionario WHERE id = {0}".format(session['user_id']))
    funcionario = cursor.fetchone()

    return render_template('admin_modificar_sucursal.html', funcionario=funcionario, sucursal=sucursal)

#------------- ACTUALIZAR SUCURSAL ROL ADMINISTRADOR ---------------
@app.route('/actualizaSucursal/<id>', methods=['POST'])
def actualizaSucursal(id):
    if request.method == 'POST':

        if 'user_id' not in session:
            return redirect(url_for('index'))

        if session['tipo'] != 2 and session['tipo'] != 3:
            return redirect(url_for('index'))

        razon_social = request.form['razon_social']
        giro = request.form['giro']
        nombre = request.form['nombre']
        rut = request.form['rut']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        correo = request.form['correo']
        estado = int(request.form['estado'])

        if estado == 1:
            estado = True
        else: 
            estado = False

        cursor.execute(
        """
        UPDATE sucursal
        SET razon_social = %s,
            giro = %s,
            nombre = %s,
            rut = %s,
            telefono = %s,
            direccion = %s,
            correo = %s,
            estado = %s
        WHERE id = %s
        """, (razon_social, giro, nombre, rut, telefono, direccion, correo, estado, id)
        )
        midb.commit()
        flash( '¡Sucursal actualizada con exito!' )
        return redirect(url_for('admin_sucursal'))
















#---------------- USUARIO CLIENTE --------------
#-------------- PAGINA TUS PEDIDOS --------------
@app.route('/tus_pedidos', methods=['POST', 'GET'])
def tus_pedidos():

    if 'user_id' not in session:
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM cliente WHERE id = '%s'" %session['user_id'] )
    cliente = cursor.fetchone()
    cursor.execute("SELECT * FROM pedido WHERE id_cliente = '%s'" %cliente['id'] )
    pedidos = cursor.fetchall()

    if pedidos != []:
        z = 0
        while z < len(pedidos):
            cursor.execute("SELECT * FROM pedido_producto WHERE id_pedido = {0}".format(pedidos[z]['id'] ))
            pedido_producto = cursor.fetchall()

            x = 0
            nombre_producto = []

            while x < len(pedido_producto):
                cursor.execute("SELECT * FROM producto WHERE id = {0}".format(pedido_producto[x]['id_producto'] ))
                producto = cursor.fetchone()                
                nombre_producto.append({
                    'nombre': producto['nombre'],
                    'cantidad': pedido_producto[x]['cantidad']
                })
                # if nombre_producto == '':
                #     nombre_producto = producto['nombre']
                # else:
                #     nombre_producto = nombre_producto + ' - ' + producto['nombre']

                x += 1   
            pedidos[z]['nombres'] = nombre_producto



            cursor.execute("SELECT * FROM sucursal WHERE id = {0}".format(pedidos[z]['id_sucursal']))
            sucursal = cursor.fetchone()
            pedidos[z]['sucursal'] = sucursal['direccion']

            cursor.execute("SELECT * FROM funcionario WHERE id = '%s'" %pedidos[z]['id_repartidor'] )
            repartidor = cursor.fetchone()
            if repartidor != None:
                pedidos[z]['repartidor'] = repartidor['nombre'] + ' ' + repartidor['apellido']

            a = reversed(pedidos)
            
            z += 1
    else:
        a = pedidos
      

    return render_template('tus_pedidos.html', cliente = cliente, pedidos=a)

#-------------- CARGAR PAGINA PEDIR --------------
@app.route('/pedir', methods=['POST', 'GET'])
def pedir():

    cursor.execute("SELECT * FROM categoria WHERE estado = 1")
    categorias = cursor.fetchall()

    prodcutos = []
    for cat in categorias:
        cursor.execute("SELECT * FROM producto WHERE estado = 1 AND cant_tienda > 0 and categoria = '%s'" %cat['id'])
        p = cursor.fetchall()
        prodcutos.append(p)


    cursor.execute('SELECT * FROM producto WHERE estado = 1 AND cant_tienda > 0')
    productos = cursor.fetchall()

    if '_flashes' in session:
        if 'user_id' not in session:
            return render_template('pedir.html', data=productos, cliente = None, categorias=categorias)

        else:
            cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
            cliente = cursor.fetchone()
            return render_template('pedir.html', data=productos, cliente = cliente, categorias=categorias)

    else:
        if 'user_id' not in session:
            return render_template('pedir.html', data=productos, cliente = None, categorias=categorias)

        else:
            cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
            cliente = cursor.fetchone()
            return render_template('pedir.html', data=productos, cliente = cliente, categorias=categorias)

#---------- DISPARA ALERTA PARA SELECCIONAR CANTIDAD DESEADA A COMPRAR -----------
@app.route('/alerta_carro/<int:id>', methods=['POST', 'GET'])
def alerta_carro(id):
    cursor.execute("SELECT * FROM producto WHERE id = {0}".format(id))
    producto = cursor.fetchone()

    for buscar_id in carro:
        if producto['id'] == buscar_id['id']:
            flash('El producto ya existe en el carro de compras')
            return redirect(url_for('pedir'))        
        

    prod = []
    prod.append(producto['id'])
    prod.append(producto['cant_tienda'])
    flash(prod)
    return redirect(url_for('pedir'))

#---------- ENVIA CANTIDAD DEL PRODUCTO SELECCIONADO
#---------------------- AL CARRO DE COMPRAS -----------
@app.route('/agregar_carro', methods=['POST', 'GET'])
def agregar_carro():

    id = request.form['id']
    cantidad = int(request.form['cantidad'])

    cursor.execute("SELECT * FROM producto WHERE id = '%s'" %id)
    producto = cursor.fetchone()

    if producto['cant_tienda'] < cantidad:
        return 'productos insuficientes'
    else:

        total = cantidad * producto['precio']
        precio_total.append(total)

        producto["cantidad"] = cantidad
        carro.append(producto)

    return redirect(url_for('pedir'))

# @app.route('/pedir_sucursal', methods=['POST', 'GET'])
# def pedir_sucursal():

#     if request.method == 'POST':

#         sucursal = int(request.form['sucursal'])
        
#         if sucursal == 99:
#             session.pop('id_sucursal', None)
#             return redirect(url_for('pedir'))

#         if 'id_sucursal' not in session:
#             session['id_sucursal'] = sucursal
#             return redirect(url_for('pedir'))

#         else:
#             session.pop('id_sucursal', None)
#             session['id_sucursal'] = sucursal
#             return redirect(url_for('pedir'))














#---------------- USUARIO CLIENTE --------------
#---------- PAGINA CARRO DE COMPRAS -----------
@app.route('/carro_compras', methods=['POST', 'GET'])
def carro_compras():

    total = sum(precio_total)

    if 'user_id' not in session:
        return render_template('carro_compras.html', data=carro, data2=total, cliente = None)
    
    else:
        cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id']))
        cliente = cursor.fetchone()
        return render_template('carro_compras.html', data=carro, data2=total, cliente = cliente)

#---------- ELIMINAR PRODUCTO DEL CARRO COMPRAS -----------
@app.route('/eliminar_de_carro/<int:id>', methods=['POST', 'GET'])
def eliminar_de_carro(id):

    if carro != []:
        prod = next((i for i, x in enumerate(carro) if x["id"] == id))
        prod2 = next(x for x in carro if x["id"] == id)
    
        valor = int(prod2["cantidad"]) * int(prod2["precio"])
    
        precio_total.remove(valor)
        carro.pop(prod)
        return redirect(url_for('carro_compras'))
    else:
        return redirect(url_for('carro_compras'))

#---------- MODIFICAR PRODUCTOS DEL CARRO COMPRAS -----------
@app.route('/modificar_carro/<int:id>', methods=['POST', 'GET'])
def modificar_carro(id):
    cursor.execute("SELECT * FROM producto WHERE id = {0}".format(id))
    producto = cursor.fetchone()
    prod = []
    prod.append(producto['id'])
    prod.append(producto['cant_tienda'])
    flash(prod)
    return redirect(url_for('carro_compras'))


@app.route('/precio_total', methods=['POST'])
async def precio():

    xxx = request.form['total']
    return xxx


#---------- VALIDAR LA COMPRA ------------
@app.route('/pagar_carro_compras', methods=['POST'])
async def pagar_carro_compras():
    
   if request.method == 'POST':
        
        if carro == []:
            flash('El carro de compras esta vacio')
            return redirect(url_for('carro_compras'))

        if 'user_id' not in session:

            cursor.execute("SELECT * FROM cliente")
            clientes = cursor.fetchall()
            mayor = 0
            for cliente in clientes:
                if mayor == 0:
                    mayor = cliente['id']
                else:
                    mayor = cliente['id'] if cliente['id'] > mayor else mayor


            id = mayor + 1
            nombre = request.form.get('nombre', type=str).capitalize()
            apellido = request.form.get('apellido', type=str).capitalize()
            rut = request.form.get('rut', type=str).capitalize()
            telefono = request.form.get('telefono', type=int)
            direccion = request.form.get('direccion', type=str)
            password = request.form.get('password', type=str)
            r_password = request.form.get('r_password', type=str)
            correo = request.form.get('correo', type=str)
            observaciones = request.form.get('observaciones', type=str)

            # VALIDAR RUT
            #--------------------------------------------
            i = 0
            if rut.count('-') != 1 or rut.count('k') > 1:
                i = 2
            else:
                if len(rut) == 10:
                    if rut.find('k') == -1 or rut.find('k') == 9:
                        if rut.find('-') != 8:
                            i = 2
                    else:
                        i = 2
                
                elif len(rut) == 9:
                    if rut.find('k') == -1 or rut.find('k') == 8:
                        if rut.find('-') != 7:
                            i = 2
                    else:
                        i = 2
                else:
                    i = 2
                
                for c in clientes:
                    if c['rut'] ==  rut:
                        i += 1
            #--------------------------------------------

            # VALIDAR PASSWORD
            #--------------------------------------------
            if password != r_password:
                i == 3
            #--------------------------------------------



            if i == 2:
                flash('El rut no es valido')
                return redirect(url_for('carro_compras'))
            elif i == 3:
                flash('Los password no coinciden')
                return redirect(url_for('carro_compras'))
            else:
                sql = 'INSERT INTO cliente (id, nombre, apellido, rut, telefono, direccion, correo, password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                values = (id, nombre, apellido, rut, telefono, direccion, correo, password)
                cursor.execute(sql,values)
                midb.commit()

            # INSERT A LA TABLA PEDIDO
            # ------------------------------------------
            cursor.execute("SELECT * FROM pedido")
            pedidos = cursor.fetchall()
            id_pedido = 0

            for pedido in pedidos:
                if id_pedido == 0:
                    id_pedido = pedido['id']
                else:
                    id_pedido = pedido['id'] if pedido['id'] > id_pedido else id_pedido


            fecha_ = date.today().strftime('%Y-%m-%d')
            anio = fecha_[0:4]
            mes = fecha_[5:7]
            dia = fecha_[8:11]

            id_pedido = id_pedido + 1
            estado = 1
            fecha = date(int(anio), int(mes), int(dia))
            hora = time.strftime("%H:%M")
            iva = (19 * sum(precio_total)) / 100
            neto = sum(precio_total) - iva
            bruto = sum(precio_total)
            id_cliente = id
            id_sucursal = request.form.get('id_sucursal', type=int)
            sql1 = 'INSERT INTO pedido (id, estado, fecha, hora, neto, iva, bruto, observaciones, id_sucursal, id_cliente) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values1 = (id_pedido, estado, fecha, hora, neto, iva, bruto, observaciones, id_sucursal, id_cliente)
            cursor.execute(sql1, values1)
            midb.commit()
            # ------------------------------------------

            # INSERT A LA TABLA PEDIDO_PRODUCTO
            # ------------------------------------------
            sql2 = 'INSERT INTO pedido_producto(id_pedido, id_producto, cantidad) VALUES (%s,%s,%s)'
            m = 0
            while m < len(carro):
                values2 = (id_pedido, carro[m]['id'], carro[m]['cantidad'])
                cursor.execute(sql2,values2)
                midb.commit()
                m += 1

            # ------------------------------------------

            # DESCONTAR PRODUCTOS DE LA BASE DE DATOS
            # ------------------------------------------
            i = 0
            while i < len(carro):
                cantidad_nueva = carro[i]['cant_tienda'] - carro[i]['cantidad']
                id_carro =  carro[i]['id']

                cursor.execute(
                    """ 
                    UPDATE producto 
                    SET cant_tienda = %s 
                    WHERE id = %s
                    """, (cantidad_nueva, id_carro)
                )
                midb.commit()
                i += 1
            #---------------------------------------

            carro.clear()
            precio_total.clear()
            flash('Datos correctos, se redirecciona al pago')
            return redirect(url_for('carro_compras'))

        else:
            cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id']) )
            cliente = cursor.fetchone()

            # ---- ACTUALIZA DIRECCION DEL CLIENTE -------
            direccion = request.form.get('direccion', type=str)
            cursor.execute(
                """
                UPDATE cliente
                SET direccion = %s
                WHERE id = %s
                """, (direccion, cliente['id'])
            )
            midb.commit()

            # ------------------------------------------

            # INSERT A LA TABLA PEDIDO
            # ------------------------------------------
            cursor.execute("SELECT * FROM pedido")
            pedidos = cursor.fetchall()
            
            id_pedido = 0
            if pedidos != None:

                for pedido in pedidos:
                    if id_pedido == 0:
                        id_pedido = pedido['id']
                    else:
                        id_pedido = pedido['id'] if pedido['id'] > id_pedido else id_pedido

            fecha_ = date.today().strftime('%Y-%m-%d')
            anio = fecha_[0:4]
            mes = fecha_[5:7]
            dia = fecha_[8:11]

            id_pedido = id_pedido + 1
            estado = 1
            fecha = date(int(anio), int(mes), int(dia))
            hora = time.strftime("%H:%M")
            iva = (19 * sum(precio_total)) / 100
            neto = sum(precio_total) - iva

            observaciones = request.form.get('observaciones', type=str)
            id_sucursal = request.form.get('id_sucursal', type=int)
            valor_envio = request.form.get('valor_envio2', type=int)

            bruto = sum(precio_total) + valor_envio

            id_cliente = cliente['id']

            sql1 = 'INSERT INTO pedido (id, estado, fecha, hora, neto, iva, bruto, observaciones, id_sucursal, id_cliente) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            values1 = (id_pedido, estado, fecha, hora, neto, iva, bruto, observaciones, id_sucursal, id_cliente)
            cursor.execute(sql1, values1)
            midb.commit()
            # ------------------------------------------
            # INSERT A LA TABLA PEDIDO_PRODUCTO
            # ------------------------------------------

            sql2 = 'INSERT INTO pedido_producto(id_pedido, id_producto, cantidad) VALUES (%s,%s,%s)'
            m = 0
            while m < len(carro):
                values2 = (id_pedido, carro[m]['id'], carro[m]['cantidad'])
                cursor.execute(sql2,values2)
                midb.commit()
                m += 1

            # ------------------------------------------

            # DESCONTAR PRODUCTOS DE LA BASE DE DATOS
            # ------------------------------------------
            i = 0
            while i < len(carro):
                cantidad_nueva = carro[i]['cant_tienda'] - carro[i]['cantidad']
                id_carro =  carro[i]['id']

                cursor.execute(
                """ 
                UPDATE producto 
                SET cant_tienda = %s 
                WHERE id = %s
                """, (cantidad_nueva, id_carro)
                )
                midb.commit()
                i += 1
            #---------------------------------------    

            carro.clear()
            precio_total.clear()
            flash('Datos correctos, se redirecciona al pago')
            return redirect(url_for('carro_compras'))
 

@app.route('/modificar_prod', methods=['POST', 'GET'])
def modificar_prod():
 if request.method == 'POST':
    id = int(request.form['id'])
    cantidad = int(request.form['cantidad'])

    prod = next((i for i, x in enumerate(carro) if x["id"] == id))
    prod2 = next(x for x in carro if x["id"] == id)
        
    valor = int(prod2["cantidad"]) * int(prod2["precio"])

    precio_total.remove(valor)
    carro.pop(prod)

    cursor.execute("SELECT * FROM producto WHERE id = '%s'" %id)
    producto = cursor.fetchone()

    if producto['cant_tienda'] < cantidad:
        return 'productos insuficientes'
    else:
        total = cantidad * producto['precio']
        precio_total.append(total)

        producto["cantidad"] = cantidad
        carro.append(producto)

        redirect(url_for('pedir'))
        return render_template('carro_compras.html')








#---------- LOCALES -----------
@app.route('/locales', methods=['POST', 'GET'])
def locales():

    cursor.execute("SELECT * FROM sucursal")
    sucursales = cursor.fetchall()
    
    if 'user_id' not in session:
        return render_template('locales.html', data=sucursales, cliente = None)
    else:
        cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
        cliente = cursor.fetchone()        
        return render_template('locales.html', data=sucursales, cliente = cliente)

#---------- NOSOTROS -----------
@app.route('/nosotros', methods=['POST', 'GET'])
def nosotros():

    if 'user_id' not in session:
        return render_template('nosotros.html', cliente = None)
    else:
        cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
        cliente = cursor.fetchone()        
        return render_template('nosotros.html', cliente = cliente)

#---------- CONTACTO -----------
@app.route('/contacto', methods=['POST', 'GET'])
def contacto():

    if 'user_id' not in session:
        return render_template('contacto.html', cliente = None)
    else:
        cursor.execute("SELECT * FROM cliente WHERE id = {0}".format(session['user_id'] ))
        cliente = cursor.fetchone()        
        return render_template('contacto.html', cliente = cliente)
















if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)