"""Usuario Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, Spacer, Label

class ProyectoForm(TableForm):

    opciones_estado = [x for x in enumerate((
        'Abierto', 'Cerrado'))]

    fields = [
	TextField('nombre', label_text='* Nombre:'),
	Spacer(),
	#SingleSelectField('estado', label_text='Estado:', options=opciones_estado),
	Label(text='   Estado: definicion'),
	Spacer(),
	CalendarDatePicker('fecha', label_text='   Fecha:', date_format='%d-%m-%y', button_text = "Elegir", calendar_lang = 'es'),
	Spacer()]

    submit_text = 'Guardar'

crear_proyecto_form = ProyectoForm("crear_proyecto_form", action='crearProyecto')
