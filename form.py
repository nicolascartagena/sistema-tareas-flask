from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class FormularioTarea(FlaskForm):
    title = StringField('Titulo de la tarea')
    description = StringField('Descripción de la tarea')
    button = SubmitField('Guardar')