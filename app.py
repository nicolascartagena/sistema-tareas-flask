# Imports
import os
from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from form import FormularioTarea

# Configuraciones
directorio = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AWCxyMFuvc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(directorio, 'tarea_bd.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Conexion BD
conexion = SQLAlchemy(app)
Migrate(app, conexion)

# Modelo
class Tarea(conexion.Model):
    __tablename__ = 'Tareas'
    id = conexion.Column(conexion.Integer, primary_key=True)
    title = conexion.Column(conexion.Text)
    description = conexion.Column(conexion.Text)
    state = conexion.Column(conexion.Boolean)
    eliminated = conexion.Column(conexion.Boolean)

    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.state = False
        self.eliminated = False
    
    def __repr__(self):
        return f'Tarea: {self.title}'

# Rutas
@app.route('/')
def index():
    if session.get('message') != None:
        message = session.get('message')
        session['message'] = ''
    else:
        message = ''
    tareas = Tarea.query.all()
    return render_template('index.html', tareas=tareas, message=message)

@app.route('/agregar', methods=['GET', 'POST'])
def agregarTarea():
    formulario = FormularioTarea()
    message = ''
    if formulario.validate_on_submit():
        try:
            title = formulario.title.data
            description = formulario.description.data
            if len(title.strip()) != 0 and len(description.strip()) != 0:
                tarea = Tarea(title, description)
                print(tarea)
            else:
                raise Exception('No se completaron los valores requeridos')
            conexion.session.add(tarea)
        except Exception as e:
            conexion.session.rollback()
            message = e
        else:
            session['message'] = 'La tarea se agrego de forma exitosa'
            conexion.session.commit()
            return redirect(url_for('index'))
            
    return render_template('agregar.html', formulario=formulario, message=message)

@app.route('/detalle/<id>')
def detalle(id):
    tarea = Tarea.query.get(id)
    error = ''
    if session.get('error'):
        error = session.get('error')
        session['error'] = ''
    if tarea:
        return render_template('detalle.html', tarea=tarea, error=error)
    else:
        session['message'] = 'No se encontro la tarea'
        return redirect(url_for('index'))

@app.route('/editar/<id>', methods=['GET', 'POST'])
def editarTarea(id):
    tarea = Tarea.query.get(id)
    formulario = FormularioTarea()
    message = ''
    if tarea and not formulario.validate_on_submit():
        formulario.title.data = tarea.title
        formulario.description.data = tarea.description
    elif not tarea and not formulario.validate_on_submit():
        session['message'] = 'No se encontro la tarea'
        return redirect(url_for('index'))

    if formulario.validate_on_submit():
        try:
            formulario
            title = formulario.title.data
            description = formulario.description.data
            print('title:',title,'desc:',description)
            if len(title.strip()) != 0 and len(description.strip()) != 0:
                tarea.title = title
                tarea.description = description
            else:
                raise Exception('No se completaron los valores requeridos')
            print(tarea)
            conexion.session.add(tarea)
        except Exception as e:
            message = e
        else:
            session['message'] = 'La tarea se agrego de forma exitosa'
            conexion.session.commit()
            return redirect(url_for('index'))

    return render_template('agregar.html', formulario=formulario, message=message)

@app.route('/eliminar/<id>')
def eliminarTarea(id):
    try:
        tarea = Tarea.query.get(id)
        if tarea:
            tarea.eliminated = True
            conexion.session.add(tarea)
        else:
            session['message'] = 'No se encontro la tarea'
            return redirect(url_for('index'))
    except Exception as e:
        session['error'] = 'Sucedio un error'
        conexion.session.rollback()
        return redirect(url_for('detalle', id=tarea.id))
    else:
        conexion.session.commit()
        session['message'] = 'Se elimino la tarea'
        return redirect(url_for('index'))

@app.route('/estado/<id>')
def toggleEstado(id):
    try:
        tarea = Tarea.query.get(id)
        tarea.state = not tarea.state
        conexion.session.add(tarea)
    except Exception as e:
        conexion.session.rollback()
        session['error'] = 'Sucedio un error'
        print(e)
        return redirect(url_for('detalle', id=tarea.id))
    else:
        conexion.session.commit()
        return redirect(url_for('detalle', id=tarea.id))

@app.route('/eliminados')
def verEliminados():
    tareas = Tarea.query.filter_by(eliminated=True)
    return render_template('eliminados.html', tareas=tareas)

@app.route('/restaurar/<id>')
def restaurarTarea(id):
    try:
        tarea = Tarea.query.get(id)
        if tarea:
            tarea.eliminated = False
            conexion.session.add(tarea)
        else:
            session['message'] = 'Sucedio un error'
            return redirect(url_for('index'))
    except Exception as e:
        conexion.session.rollback()
        session['message'] = 'Sucedio un error'
        return redirect(url_for('index'))
    else:
        conexion.session.commit()
        session['message'] = 'Tarea Restaurada'
        return redirect(url_for('index'))

@app.route('/borrar/<id>')
def borrarTarea(id):
    try:
        tarea = Tarea.query.get(id)
        conexion.session.delete(tarea)
    except Exception as e:
        session['message'] = 'A ocurrido un error'
        conexion.session.rollback()
        return redirect(url_for('index'))
    else:
        session['message'] = 'Tarea eleminada permanentemente'
        conexion.session.commit()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0")