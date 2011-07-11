"""Archivo Externo Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, Spacer, Label, HiddenField, FileField

class ArchivoExternoForm(TableForm):

    #opciones_estado = [x for x in enumerate((
    #    'Abierto', 'Cerrado'))]

    fields = [
	#TextField('vinculo', label_text='Vinculo:'),
	Spacer(),
	TextField('descripcion', label_text='Descripcion:'),
    FileField('vinculo' , laber_text='Archivo Externo'),
	HiddenField('proyecto_id'),
	HiddenField('fase_id'),
	HiddenField('item_id'), 
	Spacer()]
    submit_text = 'Guardar'

crear_archivo_externo_form = ArchivoExternoForm("crear_archivo_externo_form", action='/AgregarArchivoExterno')
