"""Rol Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, Spacer, Label, CheckBoxTable, Button, MultipleSelectField
from tw.forms.validators import NotEmpty
from prueba.model import DBSession, Permission


class RolForm(TableForm):

    opciones_permisos = DBSession.query(Permission.permission_id, Permission.description).filter_by(permission_type='sistema').order_by(Permission.permission_id)

    fields = [
	TextField('nombre', label_text='*Nombre:', validator=NotEmpty),
	TextArea('descripcion', label_text=' Descripcion:', attrs=dict(rows=2,cols=30)),
	Label(text='Puede seleccionar uno o mas permisos para el nuevo rol:'),
	MultipleSelectField('permiso', label_text='Permisos:', size=8, options=opciones_permisos)
    ]

    submit_text = ['Guardar']

crear_rol_form = RolForm("crear_rol_form", action='crearRol')
editar_rol_form = RolForm("editar_rol_form", action='eeditarRol')
