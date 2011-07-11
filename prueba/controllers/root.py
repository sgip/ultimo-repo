# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect, tmpl_context, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates

from prueba.lib.base import BaseController
from prueba.model import DBSession, metadata
#from prueba.model import *
#from prueba.widgets import *
from prueba.model import User, Group, Permission
from prueba.model.modelos import Proyecto, Fase, Tipoitem, Campo, Item, Relacion, Atributo, Modificacion, Revision, HistorialItem
from prueba.model.modelos import ItemHistorial, AtributoHistorial, RelacionHistorial, Lineabase, ArchivoExterno
from prueba.controllers.secure import SecureController
from prueba.widgets.rol_form import crear_rol_form, editar_rol_form
from prueba.widgets.usuario_form import crear_usuario_form 
from prueba.widgets.proyecto_form import crear_proyecto_form
from prueba.widgets.fase_form import crear_fase_form
from prueba.widgets.campo_form import crear_campo_form
from prueba.widgets.archivo_externo_form import crear_archivo_externo_form
from tw.forms.validators import NotEmpty, Int, DateValidator

from prueba.controllers.error import ErrorController
from repoze.what.predicates import not_anonymous
from repoze.what.predicates import Any, is_user, has_permission
#from prueba.lib.authz import user_can_edit

from tgext.crud import CrudRestController
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller
from sprox.formbase import EditableForm
from sprox.fillerbase import EditFormFiller

from sqlalchemy import or_, func, distinct
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
import formencode
from formencode import validators
from formencode.validators import DateConverter
from prueba.controllers.CalculoImpacto import CalculoImpacto
#from prueba.controllers import CalculoImpacto 
from prueba.controllers.Ciclos import Ciclos
#from prueba.controllers import Ciclos

#archivo externo
import shutil
import os
from pkg_resources import resource_filename

__all__ = ['RootController']

#Rol
'''class RolTable(TableBase):
    __model__ = Group
rol_table = RolTable(DBSession)

class RolTableFiller(TableFiller):
    __model__ = Group
rol_table_filler = RolTableFiller(DBSession)

class RolEditForm(EditableForm):
    __model__= Group
rol_edit_form = RolEditForm(DBSession)

class RolEditFiller(EditFormFiller):
    __model__ = Group
rol_edit_filler = RolEditFiller(DBSession)

class RolController(CrudRestController):
    model = Group
    table = rol_table
    table_filler = rol_table_filler
    new_form = crear_rol_form
    edit_filler = rol_edit_filler
    edit_form = rol_edit_form

#Usuario
class UserTable(TableBase):
    __model__ = User
    __omit_fields__ = ['_password']
user_table = UserTable(DBSession)

class UserTableFiller(TableFiller):
    __model__ = User
user_table_filler = UserTableFiller(DBSession)

class UserEditForm(EditableForm):
    __model__= User
    __omit_fields__ = ['_password']
user_edit_form = UserEditForm(DBSession)

class UserEditFiller(EditFormFiller):
    __model__ = User
user_edit_filler = UserEditFiller(DBSession)

class UserController(CrudRestController):
    model = User
    table = user_table
    table_filler = user_table_filler
    new_form = crear_usuario_form
    edit_filler = user_edit_filler
    edit_form = user_edit_form

#Proyecto
class ProyectoTable(TableBase):
    __model__ = Proyecto
proyecto_table = ProyectoTable(DBSession)

class ProyectoTableFiller(TableFiller):
    __model__ = Proyecto
proyecto_table_filler = ProyectoTableFiller(DBSession)

class ProyectoEditForm(EditableForm):
    __model__= Proyecto
proyecto_edit_form = ProyectoEditForm(DBSession)

class ProyectoEditFiller(EditFormFiller):
    __model__ = Proyecto
proyecto_edit_filler = ProyectoEditFiller(DBSession)

class ProyectoController(CrudRestController):
    model = Proyecto
    table = proyecto_table
    table_filler = proyecto_table_filler
    new_form = crear_proyecto_form
    edit_filler = proyecto_edit_filler
    edit_form = proyecto_edit_form'''

class PwdSchema(formencode.Schema):
    nombre = validators.NotEmpty()

class RootController(BaseController):
    """
    The root controller for the prueba application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()

    #admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    #usuarios = UserController(DBSession)
    #roles = RolController(DBSession)
    #proyectos = ProyectoController(DBSession)

    @expose('prueba.templates.index')
    def index(self):
        """Handle the front-page."""
	op = ('roles', 'usuarios', 'proyectos')
        return dict(page='index', opciones=op)

    #################### INICIO_ROLES ####################
    ##### Crear rol
    @expose('prueba.templates.rol_form')
    @require(not_anonymous(msg='Debe estar logueado'))
    @require(Any(has_permission('crear_rol'), msg='Solo los usuarios con permisos pueden crear roles'))
    def NuevoRol(self, **kw):
    	"""Show form to add new movie data record."""
    	tmpl_context.form = crear_rol_form
    	return dict(modelname='Rol', value=kw)

    ##### Crear rol
    #@expose('prueba.templates.rol_edit_form')
    #def editar_rol(self, rol_id, **kw):
    #	tmpl_context.form = editar_rol_form
    #	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
    #	value = {'nombre':"", 'description':""}
    #	value['nombre']=rol.group_name
    #	value['descripcion']=rol.group_description
    #	return dict(modelname='Rol', value=value)

    @validate(crear_rol_form, error_handler=NuevoRol)
    @expose()
    def crearRol(self, **kw):
    	rol = Group()
	rol.group_name = kw['nombre']
	rol.group_description = kw['descripcion']
    	DBSession.add(rol)
	#Agregar los permisos
	permisos = kw[u'permiso']
	for permiso_id in permisos:
	    permiso = DBSession.query(Permission).filter_by(permission_id=permiso_id).one()
            permiso.groups.append(rol)
	''' Se crean los permisos de consulta, edicion y eliminacion de este rol
	
	rol = DBSession.query(Group).filter_by(group_name=kw['nombre']).one()
	
	permiso_consultar = Permission()
	permiso_consultar.permission_name='ConsultarRol' + str(rol.group_id)
	DBSession.add(permiso_consultar)

	permiso_editar = Permission()
	permiso_editar.permission_name='EditarRol' + str(rol.group_id)
	DBSession.add(permiso_editar)
	
	permiso_eliminar = Permission()
	permiso_eliminar.permission_name='EliminarRol' + str(rol.group_id)
	DBSession.add(permiso_eliminar)

	#grupo = DBSession.query(Group).filter_by(group_id='2').one()
	#permiso_editar.groups.append(grupo)
	#permiso_eliminar.groups.append(grupo)

	#Agregar los permisos de consulta, edicion y eliminacion al rol por defecto del usuario creador del rol
	identity = request.environ['repoze.who.identity']
	usuario_creador_de_usuario = identity['user']
	rol = DBSession.query(Group).filter_by(group_name='RolPorDefecto' + str(usuario_creador_de_usuario.user_id)).one()
	rol.permissions.append(permiso_consultar)
	rol.permissions.append(permiso_editar)
	rol.permissions.append(permiso_eliminar)'''
	flash("El rol fue creado con exito")
    	redirect("ListarRoles")

    @expose('prueba.templates.editar_rol')
    def EditarRol(self, rol_id, **kw):
	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
	permisos_del_rol = rol.permissions #Permisos del rol
	todos_los_permisos = DBSession.query(Permission).all() #Todos los permisos de la BD
	return dict(page='Edicion de roles', rol_id=rol_id, rol=rol, pdr= permisos_del_rol, tlp=todos_los_permisos, value=kw)

    '''@expose()
    @validate({"nombre": NotEmpty()}, error_handler=EditarRol)
    def editarRol(self, rol_id, nombre, descripcion, permisos=None, **kw):
	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
	rol.group_name = nombre
	rol.group_description = descripcion
	
	if permisos is not None:
		if not isinstance(permisos, list):
			permisos = [permisos]
		permisos = [DBSession.query(Permission).get(permiso) for permiso in permisos]
	else:
		permisos=list()
	rol.permissions = permisos
	DBSession.flush()
	flash("El rol fue actualizado con exito")
	redirect("/ListarRoles")'''

    @expose('prueba.templates.crear_rol_proyecto')
    #@require(Any(has_permission('crear_rol'), msg='Solo los usuarios con permisos pueden crear roles'))
    def NuevoRolProyecto(self,proyecto_id, **kw):
        fases = DBSession.query(Fase).filter_by(codproyecto = proyecto_id).all()
	#permisos = list()
        #for fase in fases:
        #    permisos_aux = DBSession.query(Permission).filter_by(codfase = fase.codfase).all()
        #    permisos.extend(permisos_aux)
	#########
	fases.sort()
	permisos=list()
	for fase in fases:
		perm=DBSession.query(Permission).filter_by(codfase=fase.codfase).all() 
		permisos.append(perm)
        return dict(page = 'nuevorol', permisos = permisos, proyecto_id = proyecto_id, value=kw)
    
    @expose()
    def crearRolProyecto(self, proyecto_id,**kw):
        rol = Group()
        rol.group_name = kw['nombre']
        rol.group_description = kw['descripcion']
        rol.codproyecto = proyecto_id
        DBSession.add(rol)
        #Agregar los permisos
        if 'permisos' in kw:
            permisos = kw[u'permisos']
            if not isinstance(permisos,list):
                permisos=[permisos]
            for permiso_id in permisos:
                permiso = DBSession.query(Permission).filter_by(permission_id=permiso_id).one()
                permiso.groups.append(rol)
        flash("El rol fue creado con exito")
        redirect("/ListarRolesPorProyecto/"+proyecto_id)

    @expose('prueba.templates.editar_rol_agregar')
    def EditarRolAgregarPermisos(self, rol_id, **kw):
    	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
    	permisos_del_rol = rol.permissions #Permisos del rol
    	todos_los_permisos = DBSession.query(Permission).filter_by(permission_type='sistema').all() #Todos los permisos de la BD
        permisos_no_asignados = todos_los_permisos[:]
        for tlp in todos_los_permisos:
            for pdr in permisos_del_rol:
                if tlp == pdr:
                    permisos_no_asignados.remove(tlp)
    	return dict(page='Edicion de roles', rol_id=rol_id, rol=rol, pna = permisos_no_asignados, value=kw)

    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=EditarRolAgregarPermisos)
    def editarRolAgregarPermisos(self, rol_id, nombre, descripcion, permisos=None, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_actuales = rol.permissions[:]
        rol.group_name = nombre
        rol.group_description = descripcion
        if permisos is not None:
            if not isinstance(permisos, list):
                permisos = [permisos]
            permisos = [DBSession.query(Permission).get(permiso) for permiso in permisos]
        else:
            permisos=list()
        permisos_actuales.extend(permisos)     
        rol.permissions = permisos_actuales
        DBSession.flush()
        flash("El rol fue actualizado con exito")
        redirect("/ListarRoles")
    
    @expose('prueba.templates.editar_rol_quitar')
    def EditarRolQuitarPermisos(self, rol_id, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_del_rol = rol.permissions #Permisos del rol    
        return dict(page='Edicion de roles', rol_id=rol_id, rol=rol, pdr= permisos_del_rol, value=kw)
    
    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=EditarRolQuitarPermisos)
    def editarRolQuitarPermisos(self, rol_id, nombre, descripcion, permisos=None, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_actuales = rol.permissions
        rol.group_name = nombre
        rol.group_description = descripcion
        if permisos is not None:
            if not isinstance(permisos, list):
                permisos = [permisos]
            permisos = [DBSession.query(Permission).get(permiso) for permiso in permisos]
        else:
            permisos=list()
        
        permisos_guardar = permisos_actuales[:]
        for pa in permisos_actuales:
            for p in permisos:
                if pa == p:
                    permisos_guardar.remove(pa)            
        rol.permissions = permisos_guardar
        DBSession.flush()
        flash("El rol fue actualizado con exito")
        redirect("/ListarRoles")

    @expose('prueba.templates.editar_rol_agregar_proyecto')
    def EditarRolAgregarPermisosProyecto(self, rol_id, proyecto_id, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_del_rol = rol.permissions #Permisos del rol
        # todos los permisos del proyecto
        todos_los_permisos = list()
        fases = DBSession.query(Fase).filter_by(codproyecto = proyecto_id).all()
	fases.sort()
        for fase in fases:
	    permisos=list()
            permisos_aux = DBSession.query(Permission).filter_by(codfase = fase.codfase).all()
	    for permiso in permisos_aux:
		if permiso not in permisos_del_rol:
			permisos.append(permiso)
            todos_los_permisos.append(permisos)
        return dict(page='Edicion de roles', rol_id=rol_id, rol=rol, proyecto_id = proyecto_id, permisos = todos_los_permisos, value=kw)

    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=EditarRolAgregarPermisosProyecto)
    def editarRolAgregarPermisosProyecto(self, rol_id, proyecto_id, nombre, descripcion, permisos=None, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_actuales = rol.permissions[:]
        rol.group_name = nombre
        rol.group_description = descripcion
        if permisos is not None:
            if not isinstance(permisos, list):
                permisos = [permisos]
            permisos = [DBSession.query(Permission).get(permiso) for permiso in permisos]
        else:
            permisos=list()
        permisos_actuales.extend(permisos)     
        rol.permissions = permisos_actuales
        DBSession.flush()
        flash("El rol fue actualizado con exito")
        redirect("/ListarRolesPorProyecto/"+ proyecto_id)
    
    @expose('prueba.templates.editar_rol_quitar_proyecto')
    def EditarRolQuitarPermisosProyecto(self, rol_id, proyecto_id, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_del_rol = rol.permissions #Permisos del rol
	fases=DBSession.query(Fase).filter_by(codproyecto=proyecto_id).all()
	fases.sort()
	permisos=list()
	for fase in fases:
		aux_=list()
		aux=DBSession.query(Permission).filter_by(codfase=fase.codfase).all()
		for permiso in aux:
			if permiso in permisos_del_rol:
				aux_.append(permiso)
		permisos.append(aux_)    
        return dict(page='Edicion de roles', rol_id=rol_id, proyecto_id = proyecto_id, rol=rol, permisos= permisos, value=kw)
    
    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=EditarRolQuitarPermisosProyecto)
    def editarRolQuitarPermisosProyecto(self, rol_id, proyecto_id, nombre, descripcion, permisos=None, **kw):
        rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_actuales = rol.permissions
        rol.group_name = nombre
        rol.group_description = descripcion
        if permisos is not None:
            if not isinstance(permisos, list):
                permisos = [permisos]
            permisos = [DBSession.query(Permission).get(permiso) for permiso in permisos]
        else:
            permisos=list()
        
        permisos_guardar = permisos_actuales[:]
        for pa in permisos_actuales:
            for p in permisos:
                if pa == p:
                    permisos_guardar.remove(pa)            
        rol.permissions = permisos_guardar
        DBSession.flush()
        flash("El rol fue actualizado con exito")
        redirect("/ListarRolesPorProyecto/" + proyecto_id)

    @expose()
    def EliminarRol(self, rol_id, **kw):
	DBSession.delete(DBSession.query(Group).get(rol_id))
	#DBSession.query(Permission).filter_by(permission_name=('EditarRol' + rol_id)).one()
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarRol' + rol_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarRol' + rol_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarRol' + rol_id)).one())
	redirect("/ListarRoles")

    @expose()
    def EliminarRolProyecto(self, rol_id, proyecto_id, **kw):
        rol = DBSession.query(Group).get(rol_id)
        DBSession.delete(rol)
        redirect("/ListarRoles/" + proyecto_id)

    @expose('prueba.templates.listar_roles')
    def ListarRoles(self, **kw):
	proyectos=DBSession.query(Proyecto).order_by(Proyecto.codproyecto).all()
    	roles = DBSession.query(Group).filter_by(codproyecto=None).order_by(Group.group_id)
	### Para determinar si el usuario actualmente loggeado tiene permiso para crear nuevos roles
	'''permiso_para_crear = has_permission('crear_rol')
	### Para determinar si el usuario actualmente loggeado tiene permiso para editar roles existentes
	r=list()
	editar=list()
	identity = request.environ['repoze.who.identity']
	usuario = identity['user']
	cant=0
	for rol in roles:
		permiso = 'ConsultarRol' + str(rol.group_id)
		if has_permission(permiso):
			r.append(rol)
		permiso = 'EditarRol' + str(rol.group_id)
		if has_permission(permiso):
			editar.append(True)
		else:
			editar.append(False)
		cant = cant +1
		#can_edit = has_permission(permiso)
		#print can_edit
		#checker = user_can_edit(rol.group_id)
		#can_edit = checker.is_met(request.environ)
		#if can_edit != Nonw
		#	my_list.append(True)
		#if can_edit == None
		#	my_list.append(False)
	print type(roles)
	print type(r)
	## Paginacion
	from webhelpers import paginate
	count = cant
	page = int(kw.get('page', '1'))
	currentPage = paginate.Page(r, page, item_count=count, items_per_page=5,)
	r = currentPage.items'''
	return dict(page='Listado de Roles', roles=roles, proyectos=proyectos)

    @expose('prueba.templates.listar_permisos_de_roles_sistema')
    def ListarPermisosRolesSistema(self, rol_id, *kw):
    	rol=DBSession.query(Group).filter_by(group_id=rol_id).one()
    	return dict(page='Listar permisos del rol', rol=rol)	

    @expose('prueba.templates.listar_permisos_de_roles_proyecto')
    def ListarPermisosRolesProyecto(self, proyecto_id,rol_id, *kw):
    	rol=DBSession.query(Group).filter_by(group_id=rol_id).one()
	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_del_rol = rol.permissions #Permisos del rol
	fases=DBSession.query(Fase).filter_by(codproyecto=proyecto_id).all()
	fases.sort()
	permisos=list()
	for fase in fases:
		aux_=list()
		aux=DBSession.query(Permission).filter_by(codfase=fase.codfase).all()
		for permiso in aux:
			if permiso in permisos_del_rol:
				aux_.append(permiso)
		permisos.append(aux_)    
        return dict(page='Listar permisos del rol', rol_id=rol_id, proyecto_id = proyecto_id, rol=rol, permisos= permisos, value=kw)

    @expose('prueba.templates.listar_permisos_de_roles_proyecto2')
    def ListarPermisosRolesProyecto2(self, proyecto_id,rol_id, *kw):
    	rol=DBSession.query(Group).filter_by(group_id=rol_id).one()
	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
        permisos_del_rol = rol.permissions #Permisos del rol
	fases=DBSession.query(Fase).filter_by(codproyecto=proyecto_id).all()
	fases.sort()
	permisos=list()
	for fase in fases:
		aux_=list()
		aux=DBSession.query(Permission).filter_by(codfase=fase.codfase).all()
		for permiso in aux:
			if permiso in permisos_del_rol:
				aux_.append(permiso)
		permisos.append(aux_)    
        return dict(page='Listar permisos del rol', rol_id=rol_id, proyecto_id = proyecto_id, rol=rol, permisos= permisos, value=kw)
    
    @expose('prueba.templates.listar_roles_proyecto')
    @require(Any(has_permission('crear_rol'), msg='Solo los usuarios con permisos pueden ver el listado de roles'))
    def ListarRolesPorProyecto(self,proyecto_id, **kw):
        roles = DBSession.query(Group).filter_by(codproyecto = proyecto_id).all()
        return dict(page='Listado de Roles',proyecto_id = proyecto_id, roles=roles)

    #################### FIN_ROLES ####################

    #################### INICIO_USUARIOS ####################
    ### Crear usuario
    @expose('prueba.templates.usuario_form')
    @require(not_anonymous(msg='Debe estar logueado'))
    @require(Any(has_permission('crear_usuario'), msg='Solo los usuarios con permisos pueden crear usuarios'))
    def NuevoUsuario(self, **kw):
    	"""Show form to add new movie data record."""
    	tmpl_context.form = crear_usuario_form
    	return dict(modelname='Usuario', value=kw)

    @validate(crear_usuario_form, error_handler=NuevoUsuario)
    @expose()
    def crearUsuario(self, **kw):
    	usuario = User()
	usuario.user_name = kw['nombre']
	usuario.user_fullname = kw[u'apellido']
	usuario.password = kw[u'contrasena']
	usuario.user_telefono = kw[u'telefono']
	usuario.user_direccion = kw[u'direccion']
	usuario.email_address = kw[u'email']
	DBSession.add(usuario)
	#Agregar los roles
	roles = kw[u'rol']
	for rol_id in roles:
	    rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
            rol.users.append(usuario)
	'''#Crear el rol por defecto para este usuario
	rol_por_defecto = Group()
	rol_por_defecto.group_name = 'RolPorDefecto' + str(usuario.user_id)
	DBSession.add(rol_por_defecto)
	rol_por_defecto.users.append(usuario) #Asociar el rol por defecto con el usuario
	# Se crean los permisos de consulta, edicion y eliminacion de este usuario
	permiso_consultar = Permission()
	permiso_consultar.permission_name='ConsultarUsuario' + str(usuario.user_id)
	DBSession.add(permiso_consultar)
	permiso_editar = Permission()
	permiso_editar.permission_name='EditarUsuario' + str(usuario.user_id)
	DBSession.add(permiso_editar)
	permiso_eliminar = Permission()
	permiso_eliminar.permission_name='EliminarUsuario' + str(usuario.user_id)
	DBSession.add(permiso_eliminar)
	#Asociar el rol por defecto con el usuario
	#rol_por_defecto.users.append(usuario)
	#rol_por_defecto.permissions.append()
	#Agregar los permisos de consulta, edicion y eliminacion al rol por defecto del usuario creador de usuario
	identity = request.environ['repoze.who.identity']
	usuario_creador_de_usuario = identity['user']
	rol = DBSession.query(Group).filter_by(group_name='RolPorDefecto' + str(usuario_creador_de_usuario.user_id)).one()
	rol.permissions.append(permiso_consultar)
	rol.permissions.append(permiso_editar)
	rol.permissions.append(permiso_eliminar)
	#Asignarle al usuario recien creado el permiso de consulta de sus datos
	rol_por_defecto.permissions.append(permiso_consultar)'''
    	flash("El usuario fue creado satisfactoriamente")
    	redirect("NuevoUsuario")

    @expose('prueba.templates.crear_usuario_proyecto')
    def NuevoUsuarioProyecto(self, proyecto_id, **kw):
    	roles_del_proyecto=DBSession.query(Group).filter_by(codproyecto=proyecto_id).all()
	#en caso de error de validacion al crear usuario
	if 'username' in kw:
		username=kw['username']
	else: 
		username=""
	if 'contrasena' in kw:
		contrasena=kw['contrasena']
	else: 
		contrasena=""
	if 'nombre_completo' in kw:
		nombre_completo=kw['nombre_completo']
	else: 
		nombre_completo=""
	if 'telefono' in kw:
		telefono=kw['telefono']
	else: 
		telefono=""
	if 'direccion' in kw:
		direccion=kw['direccion']
	else: 
		direccion=""
	if 'email' in kw:
		email=kw['email']
	else: 
		email=""
	if 'roles' in kw:
		rsdp=kw['roles'] #roles seleccionados del proyecto
		if not isinstance(rsdp, list):
			rsdp=[int(rsdp)]
	else:
		rsdp=list()
	print '********************************************************************************************************'
	print 'rdp='
	for rol in roles_del_proyecto:
		print rol.group_id
	print 'rsdp= '
	print rsdp
    	return dict(page='Nuevo Usuario de Proyecto', proyecto_id=proyecto_id, username=username, contrasena=contrasena, nombre_completo=nombre_completo, telefono=telefono, direccion=direccion, email=email, rsdp=rsdp, rdp=roles_del_proyecto, value=kw)

    @expose()
    @validate({"username": NotEmpty(), "contrasena": NotEmpty(), "nombre_completo": NotEmpty(), "telefono": NotEmpty(), "direccion": NotEmpty(), "email": NotEmpty(), "roles": NotEmpty()}, error_handler=NuevoUsuarioProyecto)
    def crearUsuarioProyecto(self, proyecto_id, **kw):
    	usuario = User()
	usuario.user_name = kw['username']
	usuario.user_fullname = kw[u'nombre_completo']
	usuario.password = kw[u'contrasena']
	usuario.user_telefono = kw[u'telefono']
	usuario.user_direccion = kw[u'direccion']
	usuario.email_address = kw[u'email']
	DBSession.add(usuario)
	#Agregar los roles
	roles = kw[u'roles']
	if not isinstance(roles, list):
		roles=[roles]
	for rol_id in roles:
	    rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
            rol.users.append(usuario)
    	flash("El usuario fue creado satisfactoriamente")
    	redirect("/ListarUsuariosPorProyecto/"+proyecto_id)

    @expose('prueba.templates.editar_usuario')
    def EditarUsuario(self, usuario_id, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	#roles_del_usuario = usuario.groups #Roles del usuario
	#todos_los_roles = DBSession.query(Group).filter_by(codproyecto=None).all() #Todos los roles del sistema de la BD
	return dict(page='Edicion de usuarios', usuario_id=usuario_id, usuario=usuario, value=kw)

    @expose()
    @validate({"username": NotEmpty(), "contrasena": NotEmpty(), "nombre_completo": NotEmpty(), "telefono": NotEmpty(), "direccion": NotEmpty(), "email": NotEmpty()}, error_handler=EditarUsuario)
    def editarUsuario(self, usuario_id, username, contrasena, nombre_completo, telefono, direccion, email, roles=None, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	usuario.user_name = username
	usuario.password = contrasena
	usuario.user_fullname = nombre_completo
	usuario.user_telefono = telefono
	usuario.user_direccion = direccion
	usuario.email_address = email
		
	'''if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	usuario.groups = roles '''
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuarios")

    @expose('prueba.templates.editar_usuario_proyecto')
    def EditarUsuarioProyecto(self, proyecto_id, usuario_id, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	#roles_del_usuario = usuario.groups #Roles del usuario
	#todos_los_roles = DBSession.query(Group).filter_by(codproyecto=None).all() #Todos los roles del sistema de la BD
	return dict(page='Edicion de usuarios', proyecto_id=proyecto_id, usuario_id=usuario_id, usuario=usuario, value=kw)

    @expose()
    @validate({"username": NotEmpty(), "contrasena": NotEmpty(), "nombre_completo": NotEmpty(), "telefono": NotEmpty(), "direccion": NotEmpty(), "email": NotEmpty()}, error_handler=EditarUsuario)
    def editarUsuarioProyecto(self, proyecto_id, usuario_id, username, contrasena, nombre_completo, telefono, direccion, email, roles=None, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	usuario.user_name = username
	usuario.password = contrasena
	usuario.user_fullname = nombre_completo
	usuario.user_telefono = telefono
	usuario.user_direccion = direccion
	usuario.email_address = email
		
	'''if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	usuario.groups = roles '''
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuariosPorProyecto/"+proyecto_id)

    @expose('prueba.templates.editar_usuario_agregar_roles')
    def EditarUsuarioAgregarRoles(self, usuario_id, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	todos_los_roles = DBSession.query(Group).filter_by(codproyecto=None).all() #Todos los roles del sistema de la BD
	roles=list()
	for rol in todos_los_roles:
		if rol not in roles_del_usuario:
			roles.append(rol)
	return dict(page='Edicion de usuarios', usuario_id=usuario_id, usuario=usuario, roles=roles, value=kw)

    @expose()
    def editarUsuarioAgregarRoles(self, usuario_id, roles=None, **kw):
	if 'Aceptar' in kw:
		redirect("/ListarUsuarios")
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_actuales=usuario.groups
	if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	roles_actuales.extend(roles)
	usuario.groups=roles_actuales
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuarios")
#       permisos_actuales = rol.permissions[:]

    @expose('prueba.templates.editar_usuario_agregar_roles_proyecto')
    def EditarUsuarioAgregarRolesProyecto(self, proyecto_id, usuario_id, **kw):
	proyecto=DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	roles_del_proyecto =  proyecto.roles #Todos los roles del proyecto
	roles=list()
	for rol in roles_del_proyecto:
		if rol not in roles_del_usuario:
			roles.append(rol)
	return dict(page='Edicion de usuarios', proyecto_id=proyecto_id, usuario_id=usuario_id, usuario=usuario, roles=roles, value=kw)

    @expose()
    def editarUsuarioAgregarRolesProyecto(self, proyecto_id, usuario_id, roles=None, **kw):
	if 'Aceptar' in kw:
		redirect("/ListarUsuariosPorProyecto/"+proyecto_id)
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_actuales=usuario.groups
	if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	roles_actuales.extend(roles)
	usuario.groups=roles_actuales
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuariosPorProyecto/"+proyecto_id)

    @expose('prueba.templates.editar_usuario_quitar_roles')
    def EditarUsuarioQuitarRoles(self, usuario_id, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	roles=list()
	for rol in roles_del_usuario:
		if rol.codproyecto is None:
			roles.append(rol)
	return dict(page='Edicion de usuarios', usuario_id=usuario_id, usuario=usuario, roles=roles, value=kw)

    @expose()
    def editarUsuarioQuitarRoles(self, usuario_id, roles=None, **kw):
	if 'Aceptar' in kw:
		redirect("/ListarUsuarios")
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_actuales=usuario.groups
	if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	roles_guardar=roles_actuales
	for ra in roles_actuales:
		for r in roles:
			if ra==r:
				roles_guardar.remove(ra)
	usuario.groups=roles_guardar
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuarios")

    @expose('prueba.templates.editar_usuario_quitar_roles_proyecto')
    def EditarUsuarioQuitarRolesProyecto(self, proyecto_id, usuario_id, **kw):
	proyecto=DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	roles_del_proyecto =  proyecto.roles #Todos los roles del proyecto
	roles=list()
	for rol in roles_del_usuario:
		if rol in roles_del_proyecto:
			roles.append(rol)
	return dict(page='Edicion de usuarios', proyecto_id=proyecto_id, usuario_id=usuario_id, usuario=usuario, roles=roles, value=kw)

    @expose()
    def editarUsuarioQuitarRolesProyecto(self, proyecto_id, usuario_id, roles=None, **kw):
	if 'Aceptar' in kw:
		redirect("/ListarUsuariosPorProyecto/"+proyecto_id)
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_actuales=usuario.groups
	if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	roles_guardar=roles_actuales
	for ra in roles_actuales:
		for r in roles:
			if ra==r:
				roles_guardar.remove(ra)
	usuario.groups=roles_guardar
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuariosPorProyecto/"+proyecto_id)

    @expose('prueba.templates.listar_roles_de_usuarios_sistema')
    def ListarRolesUsuariosSistema(self, usuario_id, *kw):
    	usuario=DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles=list()
	for rol in usuario.groups:
		if rol.codproyecto is None:
			roles.append(rol)
    	return dict(page='Listar roles del usuario', usuario=usuario, roles=roles)

    @expose('prueba.templates.listar_roles_de_usuarios_proyecto')
    def ListarRolesUsuariosProyecto(self, proyecto_id, usuario_id, *kw):
    	proyecto=DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	roles_del_proyecto =  proyecto.roles #Todos los roles del proyecto
	roles=list()
	for rol in roles_del_usuario:
		if rol in roles_del_proyecto:
			roles.append(rol)
    	return dict(page='Listar roles del usuario', proyecto_id=proyecto_id, usuario=usuario, roles=roles)

    @expose('prueba.templates.listar_roles_de_usuarios_proyecto2')
    def ListarRolesUsuariosProyecto2(self, proyecto_id, usuario_id, *kw):
    	proyecto=DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	roles_del_proyecto =  proyecto.roles #Todos los roles del proyecto
	roles=list()
	for rol in roles_del_usuario:
		if rol in roles_del_proyecto:
			roles.append(rol)
    	return dict(page='Listar roles del usuario', proyecto_id=proyecto_id, usuario=usuario, roles=roles)

    @expose()
    def EliminarUsuario(self, usuario_id, **kw):
	DBSession.delete(DBSession.query(User).get(usuario_id))
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Group).filter_by(group_name=('RolPorDefecto' + usuario_id)).one())
	redirect("/ListarUsuarios")

    @expose('prueba.templates.listar_usuarios')
    def ListarUsuarios(self, **kw):
    	usuarios = DBSession.query(User).order_by(User.user_id)
	return dict(page='Listado de Usuarios', usuarios=usuarios)

    @expose('prueba.templates.listar_usuarios_por_proyectos')
    def ListarUsuariosPorProyectos(self, **kw):
    	usuarios = DBSession.query(User).order_by(User.user_id)
	###############################################################################################
	roles_del_sistema = DBSession.query(Group).filter_by(codproyecto=None).all()
	usuarios_del_sistema=list()
	for rol in roles_del_sistema:
		for usuario in rol.users:
			if usuario not in usuarios_del_sistema:
				usuarios_del_sistema.append(usuario)
	u = DBSession.query(User).filter_by(groups=None).all()
	usuarios_del_sistema.extend(u)
	###############################################################################################
	proyectos=DBSession.query(Proyecto).order_by(Proyecto.codproyecto).all()
	proyectos_usuarios=list()
	for proyecto in proyectos:
		proyectos_usuarios.append(proyecto)
		usuarios_proyecto=list()
		for rol in proyecto.roles:
			for usuario in rol.users:
				if usuario not in usuarios_proyecto:
					usuarios_proyecto.append(usuario)
		proyectos_usuarios.append(usuarios_proyecto)			
	return dict(page='Listado de Usuarios', uds=usuarios_del_sistema, proyectos_usuarios=proyectos_usuarios, proyectos=proyectos)

    @expose('prueba.templates.listar_usuarios_por_proyecto')
    def ListarUsuariosPorProyecto(self, proyecto_id, **kw):
	##usuarios del proyecto
    	usuarios = DBSession.query(User).order_by(User.user_id)
	proyecto=DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	usuarios_=list()
	for rol in proyecto.roles:
		for usuario in rol.users:
			if usuario not in usuarios_:
				usuarios_.append(usuario)
	#no-usuarios del proyecto
	no_usuarios=list()
	for usuario in usuarios:
		if usuario not in usuarios_:
			no_usuarios.append(usuario)
	## Paginacion
	from webhelpers import paginate
	count = usuarios.count()
	page = int(kw.get('page', '1'))
	currentPage = paginate.Page(usuarios, page, item_count=count, items_per_page=5,)
	usuarios = currentPage.items
	### Para determinar si el usuario actualmente loggeado tiene permiso para crear nuevos roles
	permiso_para_crear = has_permission('crear_usuario')
	return dict(page='Listado de Usuarios', proyecto=proyecto, usuarios=usuarios_, no_usuarios=no_usuarios, currentPage = currentPage, p=permiso_para_crear)

    @expose('prueba.templates.listar_todos_los_roles_del_usuario')
    def ListarTodosLosRolesDelUsuario(self, usuario_id, **kw):
	usuario=DBSession.query(User).filter_by(user_id=usuario_id).one()
	##Roles del sistema
	roles_sistema=list()
	for rol in usuario.groups:
		if rol.codproyecto is None:
			roles_sistema.append(rol)
	##Roles por proyectos
	proyectos=DBSession.query(Proyecto).order_by(Proyecto.codproyecto).all()
	roles_usuario=list()
	for proyecto in proyectos:
		roles=list()
		for rol in proyecto.roles:
			if rol in usuario.groups:
				roles.append(rol)
		if roles:
			roles_usuario.append(proyecto)
			roles_usuario.append(roles)
	return dict(page='Listado de Roles de Usuarios', roles=roles_sistema, roles_usuario=roles_usuario, usuario=usuario)
    #################### FIN_USUARIOS ####################

    #################### INICIO_PROYECTOS ####################
    ### Crear proyecto
    @expose('prueba.templates.proyecto_form')
    def NuevoProyecto(self, **kw):
	tmpl_context.form = crear_proyecto_form
    	return dict(modelname='Proyecto', value=kw)

    @validate(crear_proyecto_form, error_handler=NuevoProyecto)
    @expose()
    def crearProyecto(self, **kw):
        proyecto = Proyecto()
    	proyecto.nombre = kw['nombre']
    	proyecto.estado = 'definicion'
    	proyecto.fecha = kw['fecha']
    	DBSession.add(proyecto)
    	proyecto = DBSession.query(Proyecto).filter_by(nombre=kw['nombre']).one()
    	# Se crean los permisos de consulta, edición y eliminación del proyecto
    	permiso_consultar = Permission()
    	permiso_consultar.permission_name='ConsultarProyecto' + str(proyecto.codproyecto)
    	DBSession.add(permiso_consultar)
    	permiso_editar = Permission()
    	permiso_editar.permission_name='EditarProyecto' + str(proyecto.codproyecto)
    	DBSession.add(permiso_editar)
    	permiso_eliminar = Permission()
    	permiso_eliminar.permission_name='EliminarProyecto' + str(proyecto.codproyecto)
    	DBSession.add(permiso_eliminar)
    	permiso_definir_fases = Permission()
    	permiso_definir_fases.permission_name='DefinirFases' + str(proyecto.codproyecto)
    	DBSession.add(permiso_definir_fases)
    	
    	#Agregar los permisos de consulta, edicion y eliminacion al rol por defecto del usuario creador de proyecto
    	identity = request.environ['repoze.who.identity']
    	usuario_creador_de_proyecto = identity['user']
        for rol in usuario_creador_de_proyecto.groups:
        	rol.permissions.append(permiso_consultar)
        	rol.permissions.append(permiso_editar)
        	rol.permissions.append(permiso_eliminar)
        	rol.permissions.append(permiso_definir_fases)
    	flash("El proyecto fue creado con exito")
        redirect("ListarProyectos")

    @expose('prueba.templates.definir_fases')
    def DefinirFases(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = list()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(page='Definicion de fases', proyecto_id=proyecto_id, proyecto=proyecto, fases=fases, value=kw)

    @expose('')
    def IniciarProyecto(self, proyecto_id, **kw):
        proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
        proyecto.cantfases=len(proyecto.fases)
        proyecto.estado="desarrollo"
        fases = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).order_by(Fase.codfase).all()        
        i=1
        for fase in fases:
            # Se crean los permisos por fase
            permisoEditarFase = Permission()
            permisoEditarFase.permission_name='EditarFase'+str(fase.codfase)
            permisoEditarFase.codfase = fase.codfase
            DBSession.add(permisoEditarFase)
            permisoConsultarItems = Permission()
            permisoConsultarItems.permission_name='ConsultarItems'+str(fase.codfase)
            permisoConsultarItems.codfase = fase.codfase
            DBSession.add(permisoConsultarItems)
            permisoConsultarTipoItems = Permission()
            permisoConsultarTipoItems.permission_name='ConsultarTipoItems'+str(fase.codfase)
            permisoConsultarTipoItems.codfase = fase.codfase
            DBSession.add(permisoConsultarTipoItems)
            permisoConsultarFase = Permission()
            permisoConsultarFase.permission_name='ConsultarFase'+str(fase.codfase)
            permisoConsultarFase.codfase = fase.codfase
            DBSession.add(permisoConsultarFase)
            permisoCrearItems = Permission()
            permisoCrearItems.permission_name='CrearItems'+str(fase.codfase)
            permisoCrearItems.codfase = fase.codfase
            DBSession.add(permisoCrearItems)
            permisoCrearTipoItems = Permission()
            permisoCrearTipoItems.permission_name='CrearTipoItems'+str(fase.codfase)
            permisoCrearTipoItems.codfase = fase.codfase
            DBSession.add(permisoCrearTipoItems)
            
            permisoModificarItems = Permission()            
            permisoModificarItems.permission_name='ModificarItems'+str(fase.codfase)
            permisoModificarItems.codfase = fase.codfase
            DBSession.add(permisoModificarItems)
            
            permisoModificarTipoItems = Permission()
            permisoModificarTipoItems.permission_name='ModificarTipoItems'+str(fase.codfase)
            permisoModificarTipoItems.codfase = fase.codfase
            DBSession.add(permisoModificarTipoItems)
            
            permisoEliminarItems = Permission()
            permisoEliminarItems.permission_name='EliminarItems'+str(fase.codfase)
            permisoEliminarItems.codfase = fase.codfase
            DBSession.add(permisoEliminarItems)
            
            permisoRevertirItems = Permission()
            permisoRevertirItems.permission_name='RevertirItems'+str(fase.codfase)
            permisoRevertirItems.codfase = fase.codfase
            DBSession.add(permisoRevertirItems)
            
            permisoRevivirItems = Permission()
            permisoRevivirItems.permission_name='RevivirItems'+str(fase.codfase)
            permisoRevivirItems.codfase = fase.codfase
            DBSession.add(permisoRevivirItems)
            
            permisoImportarTipoItem = Permission()
            permisoImportarTipoItem.permission_name='ImportarTipoItem'+str(fase.codfase)
            permisoImportarTipoItem.codfase = fase.codfase
            DBSession.add(permisoImportarTipoItem)
            
	    permisoGenerarLineaBase = Permission()
            permisoGenerarLineaBase.permission_name='GenerarLineaBase'+str(fase.codfase)
            permisoGenerarLineaBase.codfase = fase.codfase
            DBSession.add(permisoGenerarLineaBase)
            
            permisoConsultarLineaBase = Permission()
            permisoConsultarLineaBase.permission_name='ConsultarLineaBase'+str(fase.codfase)
            permisoConsultarLineaBase.codfase = fase.codfase
            DBSession.add(permisoConsultarLineaBase)
            
            permisoAprobarItem = Permission()
            permisoAprobarItem.permission_name='AprobarItem'+str(fase.codfase)
            permisoAprobarItem.codfase = fase.codfase
            DBSession.add(permisoAprobarItem)

            identity = request.environ['repoze.who.identity']
            usuario_administrador = identity['user']
            for rol in usuario_administrador.groups:
                rol.permissions.append(permisoEditarFase)
                rol.permissions.append(permisoConsultarItems)
                rol.permissions.append(permisoConsultarTipoItems)
                rol.permissions.append(permisoConsultarFase)
                rol.permissions.append(permisoCrearItems)
                rol.permissions.append(permisoCrearTipoItems)
                rol.permissions.append(permisoModificarItems)
                rol.permissions.append(permisoModificarTipoItems)
                rol.permissions.append(permisoEliminarItems)
                rol.permissions.append(permisoRevertirItems)
                rol.permissions.append(permisoRevivirItems)
                rol.permissions.append(permisoImportarTipoItem)
		rol.permissions.append(permisoGenerarLineaBase)
                rol.permissions.append(permisoConsultarLineaBase)
                rol.permissions.append(permisoAprobarItem)
            fase.orden=i;
            if i==1:
                fase.estado="desarrollo"
            else:
                fase.estado="inicial"
            i=i+1
	##crear los tipos de item basicos
	for fase in fases:
		self.CrearTipoItemBasico(proyecto_id, fase)
	##
        faseaux = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=1).one()
        permisoModificarRol = Permission()
        permisoModificarRol.permission_name='ModificarRol'+str(proyecto_id)
        permisoModificarRol.codfase = fase.codfase
        DBSession.add(permisoModificarRol)   
        identity = request.environ['repoze.who.identity']
        usuario_administrador = identity['user']
        #usuario_administrador.groups
        for rol in usuario_administrador.groups:
            rol.permissions.append(permisoModificarRol)
        redirect("/ListarProyectos")

    @expose('prueba.templates.ingresar_proyecto')
    def IngresarProyecto(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(modelname='Proyecto', proyecto=proyecto, fases=fases, value=kw)

    @expose('prueba.templates.ingresar__proyecto')
    def Ingresar_Proyecto(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	fases.sort()
	return dict(modelname='Proyecto', proyecto=proyecto, fases=fases, value=kw)

    '''@expose()
    def EliminarProyecto(self, proy_id, **kw):
	proyecto = DBSession.query(Proyecto).get(proy_id)
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	for fase in fases:
		DBSession.delete(fase)	
	DBSession.delete(DBSession.query(Proyecto).get(proy_id))
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarProyecto' + proy_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarProyecto' + proy_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarProyecto' + proy_id)).one())
	redirect("/ListarProyectos/")'''

    @expose('prueba.templates.listar_proyectos')
    def ListarProyectos(self, **kw):
    	proyectos = DBSession.query(Proyecto).order_by(Proyecto.codproyecto)
	## Paginacion
	from webhelpers import paginate
	count = proyectos.count()
	page = int(kw.get('page', '1'))
	currentPage = paginate.Page(proyectos, page, item_count=count, items_per_page=5,)
	proyectos = currentPage.items
	### Para determinar si el usuario actualmente loggeado tiene permiso para crear nuevos roles
	permiso_para_crear = has_permission('crear_usuario')
	return dict(page='Listado de Proyectos', proyectos=proyectos, currentPage = currentPage, p=permiso_para_crear,permiso='crear_proyecto')  

    #################### INICIO_FASES ####################
    ### Crear fase
    @expose('prueba.templates.crear_fase')
    def NuevaFase(self, proy_id, **kw):
	nombre="" 
	descripcion=""
	if ('nombre' in kw or 'description' in kw):
		nombre=kw['nombre']
		descripcion=kw['descripcion'] 
	return dict(page='Creacion de Fases', proy_id=proy_id, nombre=nombre, descripcion=descripcion, value=kw)

    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=NuevaFase)
    def crearFase(self, proy_id, **kw):
	fase = Fase()
	fase.nombre = kw['nombre']
	fase.descripcion = kw['descripcion']
	fase.estado = "definicion"
	import datetime
	fase.fecha = datetime.date.today()
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proy_id).one()
	fase.proyecto = proyecto
	proyecto.fases.append(fase)
	#fase.codproyecto=int(proy_id)
	DBSession.add(fase)
	#self.CrearTipoItemBasico(proy_id, fase)
    	flash("La fase fue creada con exito")
    	redirect("/DefinirFases/"+proy_id)

    @expose('prueba.templates.ingresar_fase')
    def IngresarFase(self, proyecto_id, fase_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = proyecto.fases
	fases.sort()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	items = fase.items
	items.sort()
	if not isinstance(items, list):
		items = [items]
	return dict(modelname='Proyecto', proyecto=proyecto, fases=fases, fase=fase, items=items, value=kw)
    
    @expose()
    def CrearTipoItemBasico(self, proyecto_id, fase):
	print 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
	print fase.nombre
	print fase.codfase
	print fase.orden
	t = Tipoitem()
	t.nombre='Basico'
	t.fase=fase
	t.codificacion='BAS'+str(fase.orden)
	t.ultimo=0
	DBSession.add(t)

    @expose('prueba.templates.editar_fase')
    def EditarFase(self, proyecto_id, fase_id, **kw):
	fase=Fase()
	if ('nombre' in kw or 'description' in kw):
		fase.nombre=kw['nombre']
		fase.descripcion=kw['descripcion'] 
	else:
		fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	#roles_del_usuario = usuario.groups #Roles del usuario
	#todos_los_roles = DBSession.query(Group).all() #Todos los roles de la BD
	return dict(page='Edicion de fases', fase_id=fase_id, proy_id=proyecto_id, fase=fase, value=kw)

    @expose()
    @validate({"nombre": NotEmpty(),}, error_handler=EditarFase)
    def editarFase(self, proy_id, fase_id, nombre="", descripcion="", **kw):
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	fase.nombre = nombre
	fase.descripcion = descripcion
	DBSession.flush()
	flash("La fase fue actualizada con exito")
	redirect("/DefinirFases/"+proy_id)

    @expose()
    def EliminarFase(self, proy_id, fase_id, **kw):
	DBSession.delete(DBSession.query(Fase).get(fase_id))
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Group).filter_by(group_name=('RolPorDefecto' + usuario_id)).one())
	redirect("/DefinirFases/"+proy_id)

    #################### INICIO_TIPO_ITEMS ####################
    ### Crear Tipo de Ítems
    @expose('prueba.templates.crear_tipoitem')
    def NuevoTipoDeItem(self, proyecto_id, fase_id, nombre="", codificacion=None, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()	
	if 'nombre' in kw:
		nombre=kw['nombre']
	if 'codificacion' in kw:
		codificacion=kw['codificacion']
	return dict(page='Creacion de tipos de item', proyecto=proyecto, fase=fase, nombre=nombre, codificacion=codificacion, value=kw)

    @expose()
    @validate({"nombre": NotEmpty(), "codificacion": NotEmpty()}, error_handler=NuevoTipoDeItem)
    def crearTipoDeItem(self, proyecto_id, fase_id, **kw):
	tipoitem = Tipoitem()
	tipoitem.nombre = kw['nombre']
	tipoitem.codificacion=kw['codificacion']
	tipoitem.ultimo=0
	tipoitem.fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	DBSession.add(tipoitem)
	tipoitem_id = DBSession.query(Tipoitem.codtipoitem).filter_by(nombre=kw['nombre']).one()
	tipoitem_id = int(tipoitem_id[0])
	redirect("/CamposTipoDeItem/"+str(proyecto_id)+"/"+str(fase_id)+"/"+str(tipoitem_id))
	
    @expose('prueba.templates.crear_campos_tipoitem')
    def CamposTipoDeItem(self, proyecto_id, fase_id, tipoitem_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	tipoitem = DBSession.query(Tipoitem).filter_by(codtipoitem=tipoitem_id).one()
	if 'nombre' and 'tipo' in kw:
		campo = Campo()
		campo.nombre=kw['nombre']
		campo.tipo=kw['tipo']
		campo.tipoitem = tipoitem
		DBSession.add(campo)
	campos = tipoitem.campos
	if not isinstance(campos, list):
		campos=[campos]
	#nombre=""
	#atributos=list()	
	#if 'nombre' in kw:
	#	nombre=kw['nombre']
	#if 'atributos' in kw:
	#	if not isinstance(fases, list):
	#		atributos=[atributos]
	#	atributos=atributos
	return dict(page='Creacion de tipos de item', proyecto=proyecto, fase=fase, tipoitem=tipoitem, campos=campos, value=kw)
    
    @expose('prueba.templates.tipos_de_items')
    def TipoDeItem(self, proyecto_id, fase_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(page='Tipos de item', proyecto=proyecto, fases=fases, fase=fase, value=kw)

    @expose('prueba.templates.campo_form')
    def NuevoCampo(self, proyecto_id, fase_id, **kw):
    	tmpl_context.form = crear_campo_form
    	return dict(modelname='Campo de Tipo de Item', value=kw)

    @expose('prueba.templates.elegir_tipoitem')
    def ElegirTipoItem(self, proyecto_id, fase_id, **kw):
	tipos_item = DBSession.query(Tipoitem).filter_by(codfase=fase_id).all()
	if not isinstance(tipos_item, list):
		tipos_item = [tipos_item]
	return dict(page='Creacion de Items', proyecto_id=proyecto_id, fase_id=fase_id, tipos_item=tipos_item, value=kw)

    @expose('prueba.templates.crear_item')
    def NuevoItem(self, proyecto_id, fase_id, tipoitem_id, **kw):
	tipoitem = DBSession.query(Tipoitem).filter_by(codtipoitem=tipoitem_id).one()
	nombre=tipoitem.codificacion+'-'+str(tipoitem.ultimo+1)
	#en caso de error de validacion al crear item
	if 'complejidad' in kw:
		complejidad=kw['complejidad']
	else: 
		complejidad=""
	if 'prioridad' in kw:
		prioridad=kw['prioridad']
	else: 
		prioridad=""
	for campo in tipoitem.campos:
		campo.error=''
		if campo.nombre in kw:
			campo.tmp = kw[campo.nombre]
			if campo.tipo=="Integer":
				try:
					validator = validators.Int()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
			if campo.tipo=="String":
				try:
					validator = validators.String()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
			if campo.tipo=="Date":
				try:
					validator = validators.DateConverter()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
		else:
			campo.tmp = ''
	return dict(page='Creacion de Items', proyecto_id=proyecto_id, fase_id=fase_id, tipo_item=tipoitem, nombre=nombre, complejidad=complejidad, prioridad=prioridad, value=kw)

    @expose('')
    @validate({"complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=NuevoItem)
    def crearItem(self, proyecto_id, fase_id, tipoitem_id, **kw):
	print kw
	tipoitem = DBSession.query(Tipoitem).filter_by(codtipoitem=tipoitem_id).one()
	#Valida cada atributo especifico del tipo de item
	for campo in tipoitem.campos:
		if campo.nombre in kw:
			if campo.tipo=="Integer":
				validator = validators.Int()
				validator.to_python(kw[campo.nombre])
			elif campo.tipo=="String":
				validator = validators.String()
				validator.to_python(kw[campo.nombre])
			elif campo.tipo=="Date":
				validator = validators.DateConverter(month_style="dd/mm/yyyy")
				validator.to_python(kw[campo.nombre])
	##Una vez validados todos los campos, se crea el item
	tipoitem.ultimo=tipoitem.ultimo+1
	item = Item()
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=1
	item.estado='desarrollo'
	import datetime
	item.fecha=datetime.date.today()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	item.fase = fase
	item.tipoitem = tipoitem
	DBSession.add(item)
	fase.items.append(item)
	tipoitem.items.append(item)
	##Crear un atributo por cada campo del tipo de item
	for campo in tipoitem.campos:
		atributo = Atributo()
		atributo.campo = campo
		atributo.item = item
		if campo.nombre in kw:
			if campo.tipo=="Integer":
				atributo.valoratributo=kw[campo.nombre]
			elif campo.tipo=="String":
				atributo.valoratributo=kw[campo.nombre]
			elif campo.tipo=="Date":
				atributo.valoratributo=kw[campo.nombre]
		else:
			if campo.tipo=="Integer":
				atributo.valoratributo="0"
			elif campo.tipo=="String":
				atributo.valoratributo="."
			elif campo.tipo=="Date": 
				atributo.valoratributo=datetime.date.today()
		DBSession.add(atributo)
	self.crearHistorialDeItem(item)
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.consultar_item')
    def ConsultarItem(self, proyecto_id, fase_id, item_id, **kw):
	adjuntos = DBSession.query(ArchivoExterno).filter_by(coditem=item_id).all()
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	aux=DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_orden=aux[0]
	aux=DBSession.query(Proyecto.cantfases).filter_by(codproyecto=proyecto_id).one()
	cantfases = aux[0]
	##Antecesores
	items_izq_id=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo="antecesor-sucesor").all()
	items_izq_nombre=list()
	for item_izq_id in items_izq_id:
		print '****************************************************************'
		print item_izq_id
		aux = DBSession.query(Item.nombre).filter_by(coditem=item_izq_id[0]).one()
		print '****************************************************************'
		print aux
		items_izq_nombre.append(aux[0])
	##Sucesores
	items_der_id=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo="antecesor-sucesor").all()
	items_der_nombre=list()
	for item_der_id in items_der_id:
		aux = DBSession.query(Item.nombre).filter_by(coditem=item_der_id[0]).one()
		items_der_nombre.append(aux[0])
	##Padres
	items_pad_id=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo="padre-hijo").all()
	items_pad_nombre=list()
	for item_pad_id in items_pad_id:
		aux = DBSession.query(Item.nombre).filter_by(coditem=item_pad_id[0]).one()
		items_pad_nombre.append(aux[0])
	##Hijos
	items_hij_id=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo="padre-hijo").all()
	items_hij_nombre=list()
	for item_hij_id in items_hij_id:
		aux = DBSession.query(Item.nombre).filter_by(coditem=item_hij_id[0]).one()
		items_hij_nombre.append(aux[0])
	return dict(page='Consulta de items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, items_izq=items_izq_nombre, items_der=items_der_nombre, items_pad=items_pad_nombre, items_hij=items_hij_nombre, fase_orden=fase_orden, cantfases=cantfases, value=kw)

    @expose('prueba.templates.modificar_item')
    def Modificar_Item(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	##si el elemento esta en una linea base:
	if item.lineabase is not None:
		if item.lineabase.estado=='activa' or item.lineabase.estado=='comprometi':
			redirect("/ItemEnLineaBase/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	##sino:
	fase_orden = DBSession.query(Fase.orden).filter_by(codfase=fase_id).one() ##orden de la fase
	fase_orden=fase_orden[0]
	cantfases=DBSession.query(Proyecto.cantfases).filter_by(codproyecto=proyecto_id).one()
	cantfases=cantfases[0]
	return dict(page="Modificacion de items", proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id, fase_orden=fase_orden, cantfases=cantfases)

    @expose('prueba.templates.item_en_linea_base')
    def ItemEnLineaBase(self, proyecto_id, fase_id, item_id, **kw):
	return dict(page=u"Aviso: item en linea base", proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id)

    @expose('prueba.templates.item_en_linea_base_revision')
    def ItemEnLineaBaseRevision(self, proyecto_id, fase_id, item_id, **kw):
	return dict(page=u"Aviso: item en linea base", proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id)

    @expose()
    def AbrirLineaBase(self, proyecto_id, fase_id, lineabase_id, **kw):
	lineabase=DBSession.query(Lineabase).filter_by(codlineabase=lineabase_id).one()
	lineabase.estado='abierta'
	DBSession.flush()
	for item in lineabase.items:
		if item.estado=='aprobadolb':
			item.estado='aprobado'
			DBSession.flush()
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.editar_atributos')
    def ModificarAtributos(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	estado = item.estado
	#en caso de error de validacion al crear item
	if 'nombre' in kw:
		nombre = kw['nombre']
	else:	
		nombre=item.nombre
	if 'complejidad' in kw:
		complejidad=kw['complejidad']
	else: 
		complejidad=item.complejidad
	if 'prioridad' in kw:
		prioridad=kw['prioridad']
	else: 
		prioridad=item.prioridad
	campos = item.tipoitem.campos
	atributos = item.atributos
	campos.sort()
	atributos.sort()
	for i, campo in enumerate(campos):
		if i==len(atributos):
			break
		if campo.nombre in kw:
			campo.tmp = kw[campo.nombre]
			campo.error=''
			if campo.tipo=="Integer":
				try:
					validator = validators.Int()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
			if campo.tipo=="String":
				try:
					validator = validators.String()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
			if campo.tipo=="Date":
				try:
					validator = validators.DateConverter(month_style="dd/mm/yyyy")
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
		else:
			campo.tmp = atributos[i].valoratributo
			campo.error=''
	return dict(page='Edicion de Items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, estado=estado, nombre=nombre, complejidad=complejidad, prioridad=prioridad, campos=campos, value=kw)

    @expose()
    @validate({"nombre": NotEmpty(), "complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=ModificarAtributos)
    def modificarAtributos(self, proyecto_id, fase_id, item_id, **kw):
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	tipoitem = item.tipoitem
	#Valida cada atributo especifico del tipo de item
	for campo in tipoitem.campos:
		campo.tmp=''
		campo.error=''
		if campo.nombre in kw:
			if campo.tipo=="Integer":
				validator = validators.Int()
				validator.to_python(kw[campo.nombre])
			elif campo.tipo=="String":
				validator = validators.String()
				validator.to_python(kw[campo.nombre])
			elif campo.tipo=="Date":
				validator = validators.DateConverter(month_style='dd/mm/yyyy')
				validator.to_python(kw[campo.nombre])
	#Actualiza historial de item
	self.actualizarHistorialDeItem(item)
	#Actualiza atributos comunes del item
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=item.version+1 #version['version']+1
	item.estado='desarrollo'
	import datetime
	item.fecha=datetime.date.today()
	DBSession.flush()
	#Actualiza atributos especificos del tipo de item
	tipoitem.campos.sort()
	item.atributos.sort()
	cont=0 
	while(cont<len(item.atributos)):
		if tipoitem.campos[cont].nombre in kw: 
			item.atributos[cont].valoratributo=kw[tipoitem.campos[cont].nombre]
		cont=cont+1
	##Verifica si el tipo de item tiene campos nuevos
	while(cont<len(tipoitem.campos)):
		atributo = Atributo()
		atributo.campo=tipoitem.campos[cont]
		atributo.item=item
		if kw[tipoitem.campos[cont].nombre] != '':
			atributo.valoratributo=kw[tipoitem.campos[cont].nombre]
		else:
			if tipoitem.campos[cont].tipo=="Integer":
				atributo.valoratributo=0
			if tipoitem.campos[cont].tipo=="String":
				atributo.valoratributo=' '
			if tipoitem.campos[cont].tipo=="Date":
				import datetime
				atributo.valoratributo=datetime.date.today()
		DBSession.add(atributo)
		cont=cont+1
	DBSession.flush()
	self.PonerEnRevisionRelacionados(item)
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.crear_nuevo_antecesor')
    def CrearNuevoAntecesor(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	ant = DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').all()
	antecesores=list() ##lista de codigos de items
	for a in ant:
		antecesores.append(a[0])
	#hallar items de la fase anterior que no son antecesores
	fase_actual_orden = DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_anterior = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=fase_actual_orden[0]-1).one()
	todos = fase_anterior.items
	no_antecesores=list() ##lista de items
	for t in todos:
		if t.coditem not in antecesores:
			no_antecesores.append(t)	
	return dict(page="Crear nueva relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, antecesores=antecesores, no_antecesores=no_antecesores)

    @expose()
    def crearNuevoAntecesor(self, proyecto_id, fase_id, item_id, **kw):
	if 'antecesor' not in kw:
		redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	antecesor_id = int(kw['antecesor'])
	antecesor=DBSession.query(Item).filter_by(coditem=antecesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(antecesor)
	#Cambiar estado de item a 'desarrollo' y aumentar numero de version
	item.estado='desarrollo'
	item.version=item.version+1
	antecesor.version=antecesor.version+1
	DBSession.flush()
	#Crear la relacion
	relacion = Relacion()
	relacion.coditeminicio= antecesor_id
	relacion.coditemfin=item_id
	relacion.tipo='antecesor-sucesor'
	DBSession.add(relacion)
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_antecesor')
    def EliminarAntecesor(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	ant = DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').all()
	antecesores=list() ##lista de items
	for a in ant:
		aux = DBSession.query(Item).filter_by(coditem=a[0]).one()
		antecesores.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, antecesores=antecesores)

    @expose()
    def eliminarAntecesor(self, proyecto_id, fase_id, item_id, **kw):
	if 'antecesor' not in kw:
		redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	antecesor_id = int(kw['antecesor'])
	antecesor=DBSession.query(Item).filter_by(coditem=antecesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(antecesor)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	antecesor.version=antecesor.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=antecesor_id).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').one())
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.crear_nuevo_sucesor')
    def CrearNuevoSucesor(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	suc = DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='antecesor-sucesor').all()
	sucesores=list() ##lista de codigos de items
	for s in suc:
		sucesores.append(s[0])
	#hallar items de la fase anterior que no son antecesores
	fase_actual_orden = DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_posterior = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=fase_actual_orden[0]+1).one()
	todos = fase_posterior.items
	no_sucesores=list() ##lista de items
	for t in todos:
		if t.coditem not in sucesores:
			no_sucesores.append(t)	
	return dict(page="Crear nueva relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, sucesores=sucesores, no_sucesores=no_sucesores)

    @expose()
    def crearNuevoSucesor(self, proyecto_id, fase_id, item_id, **kw):
	if 'sucesor' not in kw:
		redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	sucesor_id = int(kw['sucesor'])
	sucesor=DBSession.query(Item).filter_by(coditem=sucesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(sucesor)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	sucesor.version=item.version+1
	DBSession.flush()
	#Se crea la relacion
	relacion = Relacion()
	relacion.coditeminicio= item_id
	relacion.coditemfin=sucesor_id
	relacion.tipo='antecesor-sucesor'
	DBSession.add(relacion)
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_sucesor')
    def EliminarSucesor(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	suc = DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='antecesor-sucesor').all()
	sucesores=list() ##lista de items
	for s in suc:
		aux = DBSession.query(Item).filter_by(coditem=s[0]).one()
		sucesores.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, sucesores=sucesores)

    @expose()
    def eliminarSucesor(self, proyecto_id, fase_id, item_id, **kw):
	if 'sucesor' not in kw:
		redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	sucesor_id = int(kw['sucesor'])
	sucesor=DBSession.query(Item).filter_by(coditem=sucesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(sucesor)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	sucesor.version=sucesor.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=item_id).filter_by(coditemfin=sucesor_id).filter_by(tipo='antecesor-sucesor').one())
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.establecer_relacion_misma_fase_hijo')
    def AgregarNuevoHijo(self, proyecto_id, fase_id, item_id, **kw):
        item = DBSession.query(Item).filter_by(coditem=item_id).one()
        fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()#traer items de la fase
        relacionAux = DBSession.query(Relacion).filter_by(coditeminicio=int(item_id)).filter_by(tipo='padre-hijo').all()                                                  
        itemAct = fase.items
        auxItemFase = list()
        hijos = list()
        k = 0
        
        for i in relacionAux:
            hijos.append(i.coditemfin)   
            
        for x in itemAct:
            if not x.coditem in hijos:
                auxItemFase.append(x)
                          
        print "--------------------------------------------------------------"
        for i in itemAct:   
            print i.coditem
        print "--------------------------------------------------------------"

        itemFin=list()
	tipo=0
        return dict(page='Relacion padre-hijo', proyecto_id=proyecto_id, fase_id=fase_id, item=item, itemFin=itemFin, tipo = tipo, itemAct=auxItemFase, value=kw)
    
    @expose('prueba.templates.establecer_relacion_misma_fase_padre')
    def AgregarNuevoPadre(self, proyecto_id, fase_id, item_id, **kw):
        item = DBSession.query(Item).filter_by(coditem=item_id).one()
        fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()#traer items de la fase
        relacionAux = DBSession.query(Relacion).filter_by(coditemfin=int(item_id)).filter_by(tipo='padre-hijo').all()                                                  
        itemAct = fase.items
        auxItemFase = list()
        padres = list()
        k = 0
        
        for i in relacionAux:
            padres.append(i.coditeminicio)   
            
        for x in itemAct:
            if not x.coditem in padres:
                auxItemFase.append(x)
                          
        print "--------------------------------------------------------------"
        for i in itemAct:   
            print i.coditem
        print "--------------------------------------------------------------"

        itemFin=list()
	tipo=0
        return dict(page='Relacion padre-hijo', proyecto_id=proyecto_id, fase_id=fase_id, item=item, itemFin=itemFin, tipo = tipo, itemAct=auxItemFase, value=kw)

    @expose('')
    def RelacionMismaFase(self,proyecto_id, fase_id, item_id,**kw):
	calciclo = Ciclos(int(item_id),int(kw['itemFin']))
        ciclo = calciclo.calcular()
        #boleano = calciclo.tieneAntecesor()
      
        #if boleano:
        #    print "Tiene antecesor ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ", boleano
        #else:
        #    print "No Tiene antecesor ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", boleano
            
        #si hay ciclo, informar de error al cliente y redireccionar a alguna parte
        if ciclo == 0:
	    #Actualiza historial de item
	    item=DBSession.query(Item).filter_by(coditem=item_id).one()
	    itemFin=int(kw['itemFin'])
	    itemF=DBSession.query(Item).filter_by(coditem=itemFin).one()
	    self.actualizarHistorialDeItem(item)
	    self.actualizarHistorialDeItem(itemF)
	    #Cambiar estado de item a 'espera'
	    item.estado='desarrollo'
	    item.version=item.version+1
            itemF.version=itemF.version+1
	    DBSession.flush()
	    ##Crea la relacion
            print "no hay cicloooooooo!!!!!!!!!!!!!!!!!!!11***********************"
            
            relacionNueva = Relacion()
            if int(kw['tipo']) == 1:
                relacionNueva.coditeminicio=int(item_id)
                relacionNueva.coditemfin= int(kw['itemFin'])
            else:
                relacionNueva.coditeminicio= int(kw['itemFin'])
                relacionNueva.coditemfin= int(item_id)
            relacionNueva.tipo='padre-hijo'
            DBSession.add(relacionNueva)
	    #Poner en revision items relacionados
	    self.PonerEnRevisionRelacionados(item)
                        
            flash("Relacion establecida exitosamente")
            redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)
        else:
            flash("No se permite la relacion.Un ciclo se formara con ella")   
            redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_padre')
    def EliminarPadre(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	pad = DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='padre-hijo').all()
	padres=list() ##lista de items
	for p in pad:
		aux = DBSession.query(Item).filter_by(coditem=p[0]).one()
		padres.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, padres=padres)

    @expose()
    def eliminarPadre(self, proyecto_id, fase_id, item_id, **kw):
	if 'padre' not in kw:
		redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	padre_id = kw['padre']
	padre=DBSession.query(Item).filter_by(coditem=padre_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(padre)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	padre.version=padre.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=padre_id).filter_by(coditemfin=item_id).filter_by(tipo='padre-hijo').one())
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_hijo')
    def EliminarHijo(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	hij = DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='padre-hijo').all()
	hijos=list() ##lista de items
	for h in hij:
		aux = DBSession.query(Item).filter_by(coditem=h[0]).one()
		hijos.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, hijos=hijos)

    @expose()
    def eliminarHijo(self, proyecto_id, fase_id, item_id, **kw):
	if 'hijo' not in kw:
		redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	hijo_id = kw['hijo']
	hijo=DBSession.query(Item).filter_by(coditem=hijo_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(hijo)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	hijo.version=hijo.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=item_id).filter_by(coditemfin=hijo_id).filter_by(tipo='padre-hijo').one())
	redirect("/ConsultarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.calculoimpacto')
    def CalculoImpacto(self, proyecto_id, fase_id, item_id, **kw):
	fase_orden=DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	item_nombre=DBSession.query(Item.nombre).filter_by(coditem=item_id).one()
	item_nombre=item_nombre[0]
	fase_orden=fase_orden[0]
        impactoObj = CalculoImpacto(int(item_id))
        calimpacto = impactoObj.calculoAtras()
        diccionarioListas = impactoObj.itemPorFaseImplicada()
        fases = impactoObj.codFasesImplicadas
        listaItem = list()
        for i in fases:
            listaItem.append(diccionarioListas[i])
        return dict(page='Calculo de Impacto', proyecto_id=proyecto_id, fase_id=fase_id, fase_orden=fase_orden, item_id=item_id, item_nombre=item_nombre, impacto=calimpacto, itemListas=listaItem,fases=fases, value=kw)

    @expose('prueba.templates.calculoimpactoimagen')
    def CalculoImpactoImagen(self, proyecto_id, fase_id, item_id, fase_orden,**kw):
	
        return dict(page="Grafico del calculo de impacto",proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id, fase_orden=fase_orden, value=kw)
    @expose('prueba.templates.confirmacion_eliminacion')
    def EliminarItem(self, proyecto_id, fase_id, item_id, **kw):
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	##si el elemento esta en una linea base:
	if item.lineabase is not None:
		if item.lineabase.estado=='activa' or item.lineabase.estado=='comprometi':
			redirect("/ItemEnLineaBase/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	return dict(page=u"Confirmacion de eliminación de item", proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id, item=item)

    @expose()
    def eliminarItem(self, proyecto_id, fase_id, item_id, **kw):
	if 'aceptar' in kw:
		item=DBSession.query(Item).filter_by(coditem=item_id).one()
		item.estado="eliminado"
		#Actualiza historial de item
		self.actualizarHistorialDeItem(item)
		#Poner en revision items relacionados
		self.PonerEnRevisionRelacionados(item)
		#Elimina primero las relaciones y los atributos del item
		relaciones = DBSession.query(Relacion).filter(or_(Relacion.coditeminicio==item_id, Relacion.coditemfin==item_id)).all()
		for relacion in relaciones:
			DBSession.delete(relacion)
		for atributo in item.atributos:
			DBSession.delete(atributo)
		#Elimina el item
		DBSession.delete(item)
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.listar_items_eliminados')
    def ListarItemsEliminados(self, proyecto_id, fase_id, **kw):
	items = DBSession.query(ItemHistorial).filter_by(estado="eliminado").filter_by(codfase=fase_id).all()
	return dict(page=u"Lista de ítems eliminados de la fase", proyecto_id=proyecto_id, fase_id=fase_id, items=items)

    @expose()
    def RevivirItem(self, proyecto_id, fase_id, item_id, version):
    	itemhistorial = DBSession.query(ItemHistorial).filter_by(coditem=item_id).filter_by(version=version).one()
	itemhistorial.estado="revivido"
	DBSession.flush()
	item = Item()
	##Atributos comunes 
	item.coditem=itemhistorial.coditem
	item.nombre=itemhistorial.nombre
	item.complejidad=itemhistorial.complejidad
	item.prioridad=itemhistorial.prioridad
	item.version=itemhistorial.version+1
	item.estado='desarrollo'
	import datetime
	item.fecha=datetime.date.today()
	item.codfase=itemhistorial.codfase
	item.codtipoitem=itemhistorial.codtipoitem
	DBSession.add(item)
	##Atributos específicos
	tipoitem = DBSession.query(Tipoitem).filter_by(codtipoitem=itemhistorial.codtipoitem).one()
	campos = tipoitem.campos
	atributos = itemhistorial.atributos
	print 'atributos'
	print atributos
	cont=0 
	for atrib in atributos:
		atributo=Atributo()
		atributo.codcampo=atrib.codcampo
		atributo.coditem=atrib.coditem
		atributo.valoratributo=atrib.valor
		DBSession.add(atributo)
		cont = cont+1
	if (len(campos)>cont):
		while(cont<len(campos)):
			atributo=Atributo()
			atributo.codcampo=campos[cont].codcampo
			atributo.coditem=itemhistorial.coditem
			if campos[cont].tipo=="Integer":
				atributo.valoratributo=0
			if campos[cont].tipo=="String":
				atributo.valoratributo=' '
			if campos[cont].tipo=="Date":
				import datetime
				atributo.valoratributo=datetime.date.today()
			cont=cont+1
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.editar_item')
    def ModificarItem(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	tipoitem = item.tipoitem
	###Listar items de la fase anterior y de la fase posterior
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	orden_fase = item.fase.orden
	orden_izq = orden_fase-1
	orden_der =  orden_fase+1
	items_izq=list()
	items_der=list()
	izq=list()
	der=list()
	if orden_fase > 1:
		fase_izq = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=orden_izq).one() #fase anterior
		items_izq = fase_izq.items #todos los items de la fase anterior 
		relaciones_izq = DBSession.query(Relacion).filter_by(coditemfin=item_id).all()
		for relacion in relaciones_izq:
			izq.append(relacion.coditeminicio)
		##poner en revision los antecesores
		#rel_ant = DBSession.query(Relacion).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').all()
		#print rel_ant
		#for relacion in rel_ant:
		#	item = DBSession.query(Item).get()
	if orden_fase < proyecto.cantfases:
		fase_der = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=orden_der).one()
		items_der = fase_der.items
		relaciones_der = DBSession.query(Relacion).filter_by(coditeminicio=item_id).all()
		for relacion in relaciones_der:
			der.append(relacion.coditemfin)
	#Listar ítems de la fase actual
	items_act = item.fase.items
	#relaciones_act = DBSession.query(Relacion).filter(or_(Relacion.coditeminicio=item_id, Relacion.coditemfin=item_id)).all()
	#for relacion in relaciones_act:
	#	act.append(relacion.coditeminicio)
	estado = item.estado
	return dict(page='Edicion de Items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, tipoitem=tipoitem, items_izq=items_izq, items_der=items_der, items_act=items_act, izq=izq, der=der, estado=estado, value=kw)
		
#@expose(...)
#def handle_form(self, *args, **kwargs):
#  if 'submit_foo' in kwargs:
#    return self.handle_form_foo(*args, **kwargs)
#  elif 'submit_bar' in kwargs:
#    return self.handle_form_bar(*args, **kwargs)
#def handle_form_foo(self, *args, **kwargs):
  # Do foo things
#def handle_form_bar(self, *args, **kwargs):
  # Do bar things

    @expose('prueba.templates.establecer_relacion_misma_fase')
    def RelacionarItemFase(self, proyecto_id, fase_id, item_id, **kw):
        item = DBSession.query(Item).filter_by(coditem=item_id).one()
        fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()#traer items de la fase
        itemAct = fase.items
        itemFin=list()
        return dict(page='Edicion de Items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, itemFin=itemFin, itemAct=itemAct, value=kw)
    
    @expose()
    def modificarItem(self, proyecto_id, fase_id, item_id, **kw):
	if 'modificar' in kw:
		#redirect("/editarItem/"+proyecto_id+"/"+fase_id+"/"+item_id)
		self.editarItem(proyecto_id, fase_id, item_id, **kw)
	if 'revision' in kw:
		self.editarItemPorRevision(proyecto_id, fase_id, item_id, **kw)
    @expose('')
    @validate({"nombre": NotEmpty(), "complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=ModificarItem)
    def editarItem(self, proyecto_id, fase_id, item_id, **kw):
	#Actualiza tipo de item
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#self.actualizarHistorialDeItem(item)
	#Actualiza atributos comunes del item
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=item.version+1 #version['version']+1
	#item.estado='espera'
	#import datetime
	#item.fecha=datetime.date.today()
	DBSession.flush()
	#Actualiza atributos especificos del tipo de item
	#for campo in tipoitem.campos:
	#	if campo.nombre in kw:
	#		atributo.valoratributo=kw[campo.nombre]
	#	else:
	#		if campo.tipo=="Integer":
	#			atributo.valoratributo=0
	#		if campo.tipo=="String":
	#			atributo.valoratributo=''
	#		if campo.tipo=="Date":
	#			import datetime
	#			item.fecha=datetime.date.today()
	#	DBSession.flush()
	#	print atributovalortributo
	#		DBSession.add()
	##########Guardar en la tabla 'modificacion'
	##########modificacion = Modificacion()
	##########modificacion.coditem = item.coditem
	##########modificacion.origen = 1
	##########DBSession.add(modificacion)
	##Crear las relaciones
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#print 'version'
	#print item.version
	  ## items_izq es una lista con los items seleccionados en el <select> como antecesores
	if 'items_izq' in kw: 
		items_izq = kw['items_izq']
		if not isinstance(items_izq, list):
			items_izq = [items_izq]
	else:
		items_izq=list()
	  ## items_der es una lista con los items seleccionados en el <select> como sucesores
	if 'items_der' in kw: 
		items_der = kw['items_der']
		if not isinstance(items_der, list):
			items_der = [items_der]
	else:
		items_der=list()
	for item_izq in items_izq:
		relacion = Relacion()
		relacion.coditeminicio= int(item_izq)
		relacion.coditemfin=item_id
		relacion.tipo='antecesor-sucesor'
		try:
			DBSession.query(Relacion).filter_by(coditeminicio=int(item_izq)).filter_by(coditemfin=item_id).one()
		except NoResultFound, e:
			DBSession.add(relacion)
		##Poner en revision a los items antecesores
		##########antecesor = DBSession.query(Item).filter_by(coditem=relacion.coditeminicio).one()
		##########antecesor.estado='revision'
		##########DBSession.flush()
	#	  ##Agregar a la tabla 'modificacion'
	#	##########modificacion = Modificacion()
	#	##########modificacion.coditem = relacion.coditeminicio
	#	##########modificacion.origen = 0
	#	##########DBSession.add(modificacion)
	#	  ##Agregar a la tabla 'revision'
	#	##########revision = Revision()
	#	##########revision.inicio=item.coditem
	#	##########revision.actual=relacion.coditeminicio
	#	##########revision.anterior=item.coditem
	#	##########DBSession.add(revision)
	for item_der in items_der:
		relacion = Relacion()
		relacion.coditeminicio= item_id
		relacion.coditemfin=int(item_der)
		relacion.tipo='antecesor-sucesor'
		try:
			DBSession.query(Relacion).filter_by(coditeminicio=item_id).filter_by(coditemfin=int(item_der)).one()
		except NoResultFound, e:
			DBSession.add(relacion)
	#	##Poner en revision a los items sucesores
	#	##########sucesor = DBSession.query(Item).filter_by(coditem=relacion.coditemfin).one()
	#	##########sucesor.estado='revision'
	#	##########DBSession.flush()
	#	  ##Agregar a la tabla 'modificacion'
	#	##########modificacion = Modificacion()
	#	##########modificacion.coditem = relacion.coditemfin
	#	##########modificacion.origen = 0
	#	##########DBSession.add(modificacion)
	#	  ##Agregar a la tabla 'revision'
	#	##########revision = Revision()
	#	##########revision.inicio=item.coditem
	#	##########revision.actual=relacion.coditemfin
	#	##########revision.anterior=item.coditem
	#	##########DBSession.add(revision)
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose()
    def PonerEnRevisionRelacionados(self, item):
	#Si el elemento a modificar se encuentra en una LB, esa LB pasa a estado inactiva
	#lineabase=item.lineabase
	#if lineabase is not None:
	#	lineabase.estado='inactiva'
	#	DBSession.flush()
	#	for item in lineabase.items:
	#		if item.estado=='aprobadolb'
	#			item.estado='aprobado'
	#			DBSession.flush()
	antecesores=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item.coditem).filter_by(tipo='antecesor-sucesor').all()
	for relacion in antecesores:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		lineabase=i.lineabase
		if lineabase is not None:
			if lineabase.estado=='activa':
				lineabase.estado='comprometi'
			#Agregar a la tabla 'revision'
			count1=DBSession.query(Revision).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
			count2=DBSession.query(Revision).filter_by(actual=item.coditem).filter_by(anterior=relacion[0]).count()
			if count1==0 and count2==0:
				i.estado='revision'
				DBSession.flush()
				revision = Revision()
				revision.inicio=0
				revision.actual=relacion[0]
				revision.anterior=item.coditem
				DBSession.add(revision)
	sucesores=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item.coditem).filter_by(tipo='antecesor-sucesor').all()
	for relacion in sucesores:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		lineabase=i.lineabase
		if lineabase is not None:
			if lineabase.estado=='activa':
				lineabase.estado='comprometi'
			#Agregar a la tabla 'revision'
			count1=DBSession.query(Revision).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
			count2=DBSession.query(Revision).filter_by(actual=item.coditem).filter_by(anterior=relacion[0]).count()
			if count1==0 and count2==0:
				i.estado='revision'
				DBSession.flush()
				revision = Revision()
				revision.inicio=0
				revision.actual=relacion[0]
				revision.anterior=item.coditem
				DBSession.add(revision)
	padres=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item.coditem).filter_by(tipo='padre-hijo').all()
	for relacion in padres:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		lineabase=i.lineabase
		if lineabase is not None:
			if lineabase.estado=='activa':
				lineabase.estado='comprometi'
			#Agregar a la tabla 'revision'
			count1=DBSession.query(Revision).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
			count2=DBSession.query(Revision).filter_by(actual=item.coditem).filter_by(anterior=relacion[0]).count()
			if count1==0 and count2==0:
				i.estado='revision'
				DBSession.flush()
				revision = Revision()
				revision.inicio=0
				revision.actual=relacion[0]
				revision.anterior=item.coditem
				DBSession.add(revision)
	hijos=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item.coditem).filter_by(tipo='padre-hijo').all()
	for relacion in hijos:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		lineabase=i.lineabase
		if lineabase is not None:
			if lineabase.estado=='activa':
				lineabase.estado='comprometi'
			#Agregar a la tabla 'revision'
			count1=DBSession.query(Revision).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
			count2=DBSession.query(Revision).filter_by(actual=item.coditem).filter_by(anterior=relacion[0]).count()
			if count1==0 and count2==0:
				i.estado='revision'
				DBSession.flush()
				revision = Revision()
				revision.inicio=0
				revision.actual=relacion[0]
				revision.anterior=item.coditem
				DBSession.add(revision)

    @expose('')
    @validate({"nombre": NotEmpty(), "complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=ModificarItem)
    def editarItemPorRevision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=1
	item.estado='espera'
	import datetime
	item.fecha=datetime.date.today()
	DBSession.flush()
        ##Buscar apariciones  de item_id en revision.actual
	procesos = DBSession.query(distinct(Revision.inicio)).filter_by(actual=item_id).all()
	##Crear las relaciones
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	  ## items_izq es una lista con los items seleccionados en el <select> como antecesores
	if 'items_izq' in kw: 
		items_izq = kw['items_izq']
		if not isinstance(items_izq, list):
			items_izq = [items_izq]
	else:
		items_izq=list()
	  ## items_der es una lista con los items seleccionados en el <select> como sucesores
	if 'items_der' in kw: 
		items_der = kw['items_der']
		if not isinstance(items_der, list):
			items_der = [items_der]
	else:
		items_der=list()
	cont=0
	for item_izq in items_izq:
		relacion = Relacion()
		relacion.coditeminicio= int(item_izq)
		relacion.coditemfin=item_id
		relacion.tipo='antecesor-sucesor'
		try:
			DBSession.query(Relacion).filter_by(coditeminicio=int(item_izq)).filter_by(coditemfin=item_id).one()
		except NoResultFound, e:
			DBSession.add(relacion)
		##Poner en revision a los items sucesores
		agregado = self.procesarRevision(item_id, int(item_izq), procesos)
		if agregado['agregado']==True:
			cont=cont+1
	for item_der in items_der:
		relacion = Relacion()
		relacion.coditeminicio= item_id
		relacion.coditemfin=int(item_der)
		relacion.tipo='antecesor-sucesor'
		try:
			DBSession.query(Relacion).filter_by(coditeminicio=item_id).filter_by(coditemfin=int(item_der)).one()
		except NoResultFound, e:
			DBSession.add(relacion)
		##Poner en revision a los items sucesores
		agregado = self.procesarRevision(item_id, int(item_der), procesos)
		if agregado['agregado']==True:
			cont=cont+1
	if cont==0:
		##Se eliminan las filas de revision donde revision.actual=item_id
		revisiones = DBSession.query(Revision).filter_by(actual=item_id).all()
		for revision in revisiones:
			DBSession.delete(revision)
			try:
				rev = DBSession.query(Revision).filter_by(anterior=revision.anterior).one()
			except:
				self.funcion(revision.inicio, revision.actual, revision.anterior, revision.actual)
		##Se elimina la fila de la tabla modificacion donde modificacion.coditem=item_id
		DBSession.delete(DBSession.query(Modificacion).filter_by(coditem=item_id).one())
		##Se cambia el estado al item
		item=DBSession.query(Item).filter_by(coditem=item_id).one()
		item.estado="desarrollo"
		DBSession.flush()
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)
    
    @expose()
    def crearHistorialDeItem(self, item):
	historial = HistorialItem()
	historial.coditem = item.coditem
	DBSession.add(historial)	
	return

    @expose()
    def actualizarHistorialDeItem(self, item):
	historial = DBSession.query(HistorialItem).filter_by(coditem=item.coditem).one()
	item_historial = ItemHistorial()
	item_historial.coditem=item.coditem
	item_historial.version=item.version
	item_historial.historial=historial
	item_historial.nombre=item.nombre
	item_historial.complejidad=item.complejidad
	item_historial.prioridad=item.prioridad
	item_historial.estado=item.estado
	item_historial.fecha=item.fecha
	item_historial.codtipoitem=item.codtipoitem
	item_historial.codfase=item.codfase
	DBSession.add(item_historial)
	#historial.versiones.append(item_historial)
	##Copia los atributos especificos del tipo de item
	for atributo in item.atributos:
		atributo_historial = AtributoHistorial()
		atributo_historial.coditem=item_historial.coditem
		atributo_historial.version=item_historial.version
		atributo_historial.codcampo=atributo.codcampo
		atributo_historial.valor=atributo.valoratributo
		DBSession.add(atributo_historial)
	##Copia las relaciones
	antecesores=DBSession.query(Relacion).filter_by(coditemfin=item.coditem).filter_by(tipo='antecesor-sucesor').all()
	sucesores=DBSession.query(Relacion).filter_by(coditeminicio=item.coditem).filter_by(tipo='antecesor-sucesor').all()
	padres=DBSession.query(Relacion).filter_by(coditemfin=item.coditem).filter_by(tipo='padre-hijo').all()
	hijos=DBSession.query(Relacion).filter_by(coditeminicio=item.coditem).filter_by(tipo='padre-hijo').all()
	  ##Antecesores
	for antecesor in antecesores:
		relacion_historial=RelacionHistorial()
		relacion_historial.coditem2=antecesor.coditeminicio
		item_a=DBSession.query(Item).filter_by(coditem=antecesor.coditeminicio).one()
		relacion_historial.version2=item_a.version
		relacion_historial.coditem1=item.coditem
		relacion_historial.version1=item.version
		relacion_historial.tipo='antecesor'
		DBSession.add(relacion_historial)
	  ##Sucesores
	for sucesor in sucesores:
		relacion_historial=RelacionHistorial()
		relacion_historial.coditem2=sucesor.coditemfin
		item_s=DBSession.query(Item).filter_by(coditem=sucesor.coditemfin).one()
		relacion_historial.version2=item_s.version
		relacion_historial.coditem1=item.coditem
		relacion_historial.version1=item.version
		relacion_historial.tipo='sucesor'
		DBSession.add(relacion_historial)
	  ##Padres
	for padre in padres:
		relacion_historial=RelacionHistorial()
		relacion_historial.coditem2=padre.coditeminicio
		item_p=DBSession.query(Item).filter_by(coditem=padre.coditeminicio).one()
		relacion_historial.version2=item_p.version
		relacion_historial.coditem1=item.coditem
		relacion_historial.version1=item.version
		relacion_historial.tipo='padre'
		DBSession.add(relacion_historial)
	  ##Hijos
	for hijo in hijos:
		relacion_historial=RelacionHistorial()
		relacion_historial.coditem2=hijo.coditemfin
		item_h=DBSession.query(Item).filter_by(coditem=hijo.coditemfin).one()
		relacion_historial.version2=item_h.version
		relacion_historial.coditem1=item.coditem
		relacion_historial.version1=item.version
		relacion_historial.tipo='hijo'
		DBSession.add(relacion_historial)
	return

    @expose('prueba.templates.ingresar_historial')
    def IngresarHistorial(self, proyecto_id, fase_id, item_id, **kw):
	#items = DBSession.query(ItemHistorial).filter_by(coditem=item_id).all()
	historial = DBSession.query(HistorialItem).filter_by(coditem=item_id).one()
	return dict(page='Historial de item', proyecto_id=proyecto_id, fase_id=fase_id, historial=historial, item_id=item_id, value=kw)

    @expose('prueba.templates.ingresar_historial_para_revertir')
    def IngresarHistorialParaRevertir(self, proyecto_id, fase_id, item_id, **kw):
	#items = DBSession.query(ItemHistorial).filter_by(coditem=item_id).all()
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	##si el elemento esta en una linea base:
	if item.lineabase is not None:
		if item.lineabase.estado=='activa' or item.lineabase.estado=='comprometi':
			redirect("/ItemEnLineaBase/"+proyecto_id+"/"+fase_id+"/"+item_id)	
	historial = DBSession.query(HistorialItem).filter_by(coditem=item_id).one()
	return dict(page='Historial de item', proyecto_id=proyecto_id, fase_id=fase_id, historial=historial, item_id=item_id, value=kw)

    @expose()
    def RevertirItem(self, proyecto_id, fase_id, item_id, version):
	#Guardar version actual en el historial
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	self.actualizarHistorialDeItem(item)
	#Poner en revision los items con los que esta relacionado el item antes de revertirse
	self.PonerEnRevisionRelacionados(item)
	#Traer del historial la version a revertir
	item_version_anterior = DBSession.query(ItemHistorial).filter_by(coditem=item_id).filter_by(version=version).one()
	#Actualizar atributos comunes
	item.version=item.version+1
	item.nombre=item_version_anterior.nombre
	item.complejidad=item_version_anterior.complejidad
	item.prioridad=item_version_anterior.prioridad
	#item.estado=item_version_anterior.estado
	item.estado='desarrollo'
	item.fecha=item_version_anterior.fecha
	#Actualiza atributos especificos
	atributos = item.atributos
	atributos_historial=item_version_anterior.atributos
	cont=0
	for atributo in atributos_historial:
		atributos[cont].valoratributo=atributo.valor
		cont=cont+1
	if cont < len(atributos):
		while(cont<len(atributos)):
			if atributos[cont].campo.tipo=="Integer":
				atributo[cont].valoratributo=0
			if atributos[cont].campo.tipo=="String":
				atributo[cont].valoratributo='-'
			if atributos[cont].campo.tipo=="Date":
				import datetime	
				atributo[cont].valoratributo = datetime.date.today()	
			cont=cont+1
	DBSession.flush()
	#Elimina relaciones actuales
	relaciones = DBSession.query(Relacion).filter(or_(Relacion.coditeminicio==item_id,Relacion.coditemfin==item_id)).all()
	for relacion in relaciones:
		DBSession.delete(relacion)
		print relacion
	#Recupera los antecesores de la version anterior
	antecesores = DBSession.query(RelacionHistorial.coditem2).filter_by(coditem1=item_id).filter_by(version1=version).filter_by(tipo='antecesor').all()
	for antecesor in antecesores:
		cant = DBSession.query(Item).filter_by(coditem=antecesor[0]).count()
		if cant==1:
			relacion=Relacion()
			relacion.coditeminicio=antecesor[0]
			relacion.coditemfin=item_id
			relacion.tipo='antecesor-sucesor'
			DBSession.add(relacion)
	##SUCESORES
	sucesores = DBSession.query(RelacionHistorial.coditem2).filter_by(coditem1=item_id).filter_by(version1=version).filter_by(tipo='sucesor').all()
	for sucesor in sucesores:
		cant = DBSession.query(Item).filter_by(coditem=sucesor[0]).count()
		if cant==1:
			relacion=Relacion()
			relacion.coditeminicio=item_id
			relacion.coditemfin=sucesor[0]
			relacion.tipo='antecesor-sucesor'
			DBSession.add(relacion)
	##PADRES
	padres = DBSession.query(RelacionHistorial.coditem2).filter_by(coditem1=item_id).filter_by(version1=version).filter_by(tipo='padre').all()
	for padre in padres:
		cant = DBSession.query(Item).filter_by(coditem=padre[0]).count()
		calciclo = Ciclos(int(padre[0]),int(item_id))
        	ciclo = calciclo.calcular()
		if cant==1 and ciclo==0:
			relacion=Relacion()
			relacion.coditeminicio=padre[0]
			relacion.coditemfin=item_id
			relacion.tipo='padre-hijo'
			DBSession.add(relacion)
	##HIJOS
	hijos = DBSession.query(RelacionHistorial.coditem2).filter_by(coditem1=item_id).filter_by(version1=version).filter_by(tipo='hijo').all() 
	for hijo in hijos:
		cant = DBSession.query(Item).filter_by(coditem=hijo[0]).count()
		calciclo = Ciclos(int(item_id), int(hijo[0]))
		ciclo = calciclo.calcular()
		if cant==1 and ciclo==0:
			relacion=Relacion()
			relacion.coditeminicio=item_id
			relacion.coditemfin=hijo[0]
			relacion.tipo='padre-hijo'
			DBSession.add(relacion)
	self.PonerEnRevisionNuevosRelacionados(item)
	redirect('/ConsultarItem/' + proyecto_id + '/' + fase_id + '/' + item_id)

    @expose('prueba.templates.consultar_itemhistorial')
    def ConsultarItemHistorial(self, proyecto_id, fase_id, item_id, item_version, **kw):
	#Para la informacion general
	item=DBSession.query(ItemHistorial).filter_by(coditem=item_id).filter_by(version=item_version).one()
	tipoitem=DBSession.query(Tipoitem).filter_by(codtipoitem=item.codtipoitem).one()
	#Para los atributos especificos del tipo de item
	atributos=DBSession.query(AtributoHistorial).filter_by(coditem=item_id).filter_by(version=item_version).all()
	#Para recuperar las relaciones
	aux=DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_orden=aux[0]
	aux=DBSession.query(Proyecto.cantfases).filter_by(codproyecto=proyecto_id).one()
	cantfases = aux[0]
	#print 'EMPIEZA'
	#relaciones = item.relaciones
	#for relacion in relaciones:
	#	print type(relacion)
	#	print 'relaciones'
	#	print relacion.coditem1
        #	print relacion.version1
	#	print relacion.coditem2
	#	print relacion.version2
	#	print relacion.tipo
	##Antecesores
	items_izq = DBSession.query(RelacionHistorial).filter_by(coditem1=item_id).filter_by(version1=item_version).filter_by(tipo='antecesor').all()
	##Sucesores
	items_der = DBSession.query(RelacionHistorial).filter_by(coditem1=item_id).filter_by(version1=item_version).filter_by(tipo='sucesor').all()
	##Padres
	items_pad = DBSession.query(RelacionHistorial).filter_by(coditem1=item_id).filter_by(version1=item_version).filter_by(tipo='padre').all()
	##Hijos
	items_hij = DBSession.query(RelacionHistorial).filter_by(coditem1=item_id).filter_by(version1=item_version).filter_by(tipo='hijo').all()
	return dict(page='Consulta de item historial', proyecto_id=proyecto_id, fase_id=fase_id, item=item, tipoitem=tipoitem, fase_orden=fase_orden, cantfases=cantfases, atributos=atributos, items_izq=items_izq, items_der=items_der, items_pad=items_pad, items_hij=items_hij, value=kw)

    @expose()
    def EstablecerItemListoParaAprobacion(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	self.actualizarHistorialDeItem(item)
	item.estado='listo'
	item.version=item.version+1
	DBSession.flush()
	redirect('/ConsultarItem/' + proyecto_id + "/" + fase_id + "/" + item_id)

    @expose()
    def AprobarItem(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	self.actualizarHistorialDeItem(item)
	item.estado='aprobado'
	item.version=item.version+1
	DBSession.flush()
	redirect('/ConsultarItem/' + proyecto_id + "/" + fase_id + "/" + item_id)

    @expose('prueba.templates.lineas_bases')
    def LineasBases(self, proyecto_id, fase_id, **kw):
	lineasbases = DBSession.query(Lineabase).filter_by(codfase=fase_id).filter(or_(Lineabase.estado=='activa',Lineabase.estado=='comprometi')).all()
	return dict(page=u'Líneas Base de la Fase', proyecto_id=proyecto_id, fase_id=fase_id, lineasbases=lineasbases)

    @expose()
    def lineasBases(self, proyecto_id, fase_id, **kw):
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.generar_linea_base')
    def GenerarLineaBase(self, proyecto_id, fase_id, **kw):
	#Cantidad de fases del proyecto y el orden de la fase actual
	cantfases=DBSession.query(Proyecto.cantfases).filter_by(codproyecto=proyecto_id).one()
	cantfases=cantfases[0]
	fase_actual_orden=DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_actual_orden=fase_actual_orden[0]
	#items_aprobados->todos los items aprobados de la fase
	items_aprobados = DBSession.query(Item).filter_by(codfase=fase_id).filter_by(estado='aprobado').all()
	#hacer una sublista de los items aprobados y que tengan como minimo un antecesor
	if fase_actual_orden>1:
		items=list()
		for item in items_aprobados:
			ciclo = Ciclos(item.coditem, item.coditem)
			ciclo = ciclo.tieneAntecesor()	
			if ciclo==1:
				items.append(item)
	else:
		items=items_aprobados
	return dict(page=u'Generación de Línea Base', proyecto_id=proyecto_id, fase_id=fase_id, items=items)

    @expose()
    @validate({"linea_base": NotEmpty()}, error_handler=GenerarLineaBase)
    def generarLineaBase(self, proyecto_id, fase_id, **kw):
	#Cantidad de fases del proyecto y el orden de la fase actual
	cantfases=DBSession.query(Proyecto.cantfases).filter_by(codproyecto=proyecto_id).one()
	cantfases=cantfases[0]
	fase_actual_orden=DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_actual_orden=fase_actual_orden[0]
	#items->elementos seleccionados para formar la linea base	
	items = kw['linea_base']
	if not isinstance(items, list):
		items = [items]
	#Crea la linea base
	lineabase = Lineabase()
	lineabase.codfase=fase_id
	lineabase.estado='activa'
	DBSession.add(lineabase)
	#Agrega los items a la linea base
	for item_id in items:
		item=DBSession.query(Item).filter_by(coditem=item_id).one()
		item.lineabase=lineabase
		item.estado='aprobadolb'
		DBSession.flush()
	#Habilita la siguiente fase en caso de que no este habilitada todavia
	if fase_actual_orden<cantfases:
		fase_siguiente=DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=fase_actual_orden+1).one()
		if fase_siguiente.estado=='inicial':
			fase_siguiente.estado='desarrollo'
			DBSession.flush()
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('prueba.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('prueba.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)

    @expose('prueba.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')

    @expose('prueba.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('prueba.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('prueba.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        #redirect(came_from)
	redirect("/index")

    @expose('prueba.templates.revisar_item')
    def RevisarItem(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	tipoitem = item.tipoitem
	#Antecesores
	ant=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').all()
	antecesores=list()
	for relacion in ant:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		antecesores.append(i)
	suc=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='antecesor-sucesor').all()
	#Sucesores
	sucesores=list()
	for relacion in suc:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		sucesores.append(i)
	#Padres
	pad=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='padre-hijo').all()
	padres=list()
	for relacion in pad:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		padres.append(i)
	#Hijos
	hij=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='padre-hijo').all()
	hijos=list()
	for relacion in hij:
		i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
		hijos.append(i)
	#Items que el usuario debe consultar para decidir si realizar cambios o no
	items_a_verificar=DBSession.query(Revision.anterior).filter_by(actual=item_id).all()
	items=list()
	item_eliminado=Item()
	for it in items_a_verificar:
		try:
			i=DBSession.query(Item).filter_by(coditem=it[0]).one()
			items.append(i)
		except:
		#si no encuentra, entonces se trata de un item eliminado
			item_eliminado=DBSession.query(ItemHistorial).filter_by(coditem=it[0]).filter_by(estado='eliminado').one()
	return dict(page='Revision de Items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, tipoitem=tipoitem, antecesores=antecesores, sucesores=sucesores, padres=padres, hijos=hijos, items=items, item_eliminado=item_eliminado, value=kw)

    @expose()
    def revisarItem(self, proyecto_id, fase_id, item_id, **kw):
	if 'modificar' in kw:
		item=DBSession.query(Item).filter_by(coditem=item_id).one()
		if item.lineabase.estado=='activa' or item.lineabase.estado=='comprometi':
			redirect("/ItemEnLineaBaseRevision/"+ proyecto_id +"/"+fase_id+"/"+item_id)
		else:
			redirect("/Modificar_Item_Revision/"+proyecto_id+"/"+fase_id+"/"+item_id)
	else:
		redirect("/NoModificar_Item_Revision/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose()
    def NoModificar_Item_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	if item.lineabase.estado=='comprometi':
		count=DBSession.query(Item).filter_by(codlineabase=item.codlineabase).filter_by(estado='revision').count()
		if count==1:
			item.lineabase.estado='activa'
		item.estado='aprobadolb'
	if item.lineabase.estado=='abierta':
		item.estado='aprobado'
	DBSession.flush()
	##Se eliminan las filas de revision donde revision.actual=item_id
	revisiones = DBSession.query(Revision).filter_by(actual=item_id).all()
	for revision in revisiones:
		DBSession.delete(revision)
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.modificar_item_revision')
    def Modificar_Item_Revision(self, proyecto_id, fase_id, item_id, **kw):
	fase_orden = DBSession.query(Fase.orden).filter_by(codfase=fase_id).one() ##orden de la fase
	fase_orden=fase_orden[0]
	cantfases=DBSession.query(Proyecto.cantfases).filter_by(codproyecto=proyecto_id).one()
	cantfases=cantfases[0]
	return dict(page="Modificacion de items", proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id, fase_orden=fase_orden, cantfases=cantfases)

    @expose('prueba.templates.editar_atributos_revision')
    def ModificarAtributos_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	estado = item.estado
	#en caso de error de validacion al crear item
	if 'nombre' in kw:
		nombre = kw['nombre']
	else:	
		nombre=item.nombre
	if 'complejidad' in kw:
		complejidad=kw['complejidad']
	else: 
		complejidad=item.complejidad
	if 'prioridad' in kw:
		prioridad=kw['prioridad']
	else: 
		prioridad=item.prioridad
	campos = item.tipoitem.campos
	atributos = item.atributos
	campos.sort()
	atributos.sort()
	for i, campo in enumerate(campos):
		if i==len(atributos):
			break
		if campo.nombre in kw:
			campo.tmp = kw[campo.nombre]
			campo.error=''
			if campo.tipo=="Integer":
				try:
					validator = validators.Int()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
			if campo.tipo=="String":
				try:
					validator = validators.String()
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
			if campo.tipo=="Date":
				try:
					validator = validators.DateConverter(month_style="dd/mm/yyyy")
					validator.to_python(kw[campo.nombre])
				except formencode.Invalid, e:
					campo.error=unicode(e)
		else:
			campo.tmp = atributos[i].valoratributo
			campo.error=''
	return dict(page='Edicion de Items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, estado=estado, nombre=nombre, complejidad=complejidad, prioridad=prioridad, campos=campos, value=kw)

    @expose()
    @validate({"nombre": NotEmpty(), "complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=ModificarAtributos_Revision)
    def modificarAtributos_revision(self, proyecto_id, fase_id, item_id, **kw):
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	tipoitem = item.tipoitem
	#Valida cada atributo especifico del tipo de item
	for campo in tipoitem.campos:
		campo.tmp=''
		campo.error=''
		if campo.nombre in kw:
			if campo.tipo=="Integer":
				validator = validators.Int()
				validator.to_python(kw[campo.nombre])
			elif campo.tipo=="String":
				validator = validators.String()
				validator.to_python(kw[campo.nombre])
			elif campo.tipo=="Date":
				validator = validators.DateConverter(month_style='dd/mm/yyyy')
				validator.to_python(kw[campo.nombre])
	#Actualiza historial de item
	self.actualizarHistorialDeItem(item)
	#Actualiza atributos comunes del item
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=item.version+1 #version['version']+1
	item.estado='desarrollo'
	import datetime
	item.fecha=datetime.date.today()
	DBSession.flush()
	#Actualiza atributos especificos del tipo de item
	tipoitem.campos.sort()
	item.atributos.sort()
	cont=0 
	while(cont<len(item.atributos)):
		if tipoitem.campos[cont].nombre in kw: 
			item.atributos[cont].valoratributo=kw[tipoitem.campos[cont].nombre]
		cont=cont+1
	##Verifica si el tipo de item tiene campos nuevos
	while(cont<len(tipoitem.campos)):
		atributo = Atributo()
		atributo.campo=tipoitem.campos[cont]
		atributo.item=item
		if kw[tipoitem.campos[cont].nombre] != '':
			atributo.valoratributo=kw[tipoitem.campos[cont].nombre]
		else:
			if tipoitem.campos[cont].tipo=="Integer":
				atributo.valoratributo=0
			if tipoitem.campos[cont].tipo=="String":
				atributo.valoratributo=' '
			if tipoitem.campos[cont].tipo=="Date":
				import datetime
				atributo.valoratributo=datetime.date.today()
		DBSession.add(atributo)
		cont=cont+1
	DBSession.flush()
	self.PonerEnRevisionRelacionados(item)
	#cont = self.procesarRevision(item)
	#redirect("/Modificar_Item_Revision/"+proyecto_id+"/"+fase_id+"/"+item_id)
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.confirmacion_para_seguir_modificando')
    def ConfirmacionModificacion(self, proyecto_id, fase_id, item_id, **kw):
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	return dict(page=u"Seguir modificando?", proyecto_id=proyecto_id, fase_id=fase_id, item_id=item_id, item=item)
	
    @expose()
    def confirmacionModificacion(self, proyecto_id, fase_id, item_id, **kw):
	if 'si' in kw:
		redirect("/Modificar_Item_Revision/"+proyecto_id+"/"+fase_id+"/"+item_id)
	if 'no' in kw:
		item=DBSession.query(Item).filter_by(coditem=item_id).one()
		item.estado='desarrollo'
		DBSession.flush()
		##Se eliminan las filas de revision donde revision.actual=item_id
		revisiones = DBSession.query(Revision).filter_by(actual=item_id).all()
		for revision in revisiones:
			DBSession.delete(revision)
		redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.crear_nuevo_antecesor_revision')
    def CrearNuevoAntecesor_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	ant = DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').all()
	antecesores=list() ##lista de codigos de items
	for a in ant:
		antecesores.append(a[0])
	#hallar items de la fase anterior que no son antecesores
	fase_actual_orden = DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_anterior = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=fase_actual_orden[0]-1).one()
	todos = fase_anterior.items
	no_antecesores=list() ##lista de items
	for t in todos:
		if t.coditem not in antecesores:
			no_antecesores.append(t)	
	return dict(page="Crear nueva relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, antecesores=antecesores, no_antecesores=no_antecesores)

    @expose()
    def crearNuevoAntecesor_revision(self, proyecto_id, fase_id, item_id, **kw):
	if 'antecesor' not in kw:
		redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	antecesor_id = int(kw['antecesor'])
	antecesor=DBSession.query(Item).filter_by(coditem=antecesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(antecesor)
	#Cambiar estado de item a 'espera' y aumentar numero de version
	item.version=item.version+1
	antecesor.version=antecesor.version+1
	DBSession.flush()
	#Crear la relacion
	relacion = Relacion()
	relacion.coditeminicio= antecesor_id
	relacion.coditemfin=item_id
	relacion.tipo='antecesor-sucesor'
	DBSession.add(relacion)
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_antecesor_revision')
    def EliminarAntecesor_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	ant = DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').all()
	antecesores=list() ##lista de items
	for a in ant:
		aux = DBSession.query(Item).filter_by(coditem=a[0]).one()
		antecesores.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, antecesores=antecesores)

    @expose()
    def eliminarAntecesor_revision(self, proyecto_id, fase_id, item_id, **kw):
	if 'antecesor' not in kw:
		redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	antecesor_id = int(kw['antecesor'])
	antecesor=DBSession.query(Item).filter_by(coditem=antecesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(antecesor)
	#Aumentar version
	item.version=item.version+1
	antecesor.version=antecesor.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=antecesor_id).filter_by(coditemfin=item_id).filter_by(tipo='antecesor-sucesor').one())
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.crear_nuevo_sucesor_revision')
    def CrearNuevoSucesor_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	suc = DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='antecesor-sucesor').all()
	sucesores=list() ##lista de codigos de items
	for s in suc:
		sucesores.append(s[0])
	#hallar items de la fase anterior que no son antecesores
	fase_actual_orden = DBSession.query(Fase.orden).filter_by(codfase=fase_id).one()
	fase_posterior = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=fase_actual_orden[0]+1).one()
	todos = fase_posterior.items
	no_sucesores=list() ##lista de items
	for t in todos:
		if t.coditem not in sucesores:
			no_sucesores.append(t)	
	return dict(page="Crear nueva relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, sucesores=sucesores, no_sucesores=no_sucesores)

    @expose()
    def crearNuevoSucesor_revision(self, proyecto_id, fase_id, item_id, **kw):
	if 'sucesor' not in kw:
		redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	sucesor_id = int(kw['sucesor'])
	sucesor=DBSession.query(Item).filter_by(coditem=sucesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(sucesor)
	#Aumentar version de item
	item.version=item.version+1
	sucesor.version=sucesor.version+1
	DBSession.flush()
	#Crea la relacion
	relacion = Relacion()
	relacion.coditeminicio= item_id
	relacion.coditemfin=sucesor_id
	relacion.tipo='antecesor-sucesor'
	DBSession.add(relacion)
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_sucesor_revision')
    def EliminarSucesor_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	suc = DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='antecesor-sucesor').all()
	sucesores=list() ##lista de items
	for s in suc:
		aux = DBSession.query(Item).filter_by(coditem=s[0]).one()
		sucesores.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, sucesores=sucesores)

    @expose()
    def eliminarSucesor_revision(self, proyecto_id, fase_id, item_id, **kw):
	if 'sucesor' not in kw:
		redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	sucesor_id = kw['sucesor']
	sucesor=DBSession.query(Item).filter_by(coditem=sucesor_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(sucesor)
	#Cambiar estado de item a 'espera'
	item.version=item.version+1
	sucesor.version=sucesor.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=item_id).filter_by(coditemfin=sucesor_id).filter_by(tipo='antecesor-sucesor').one())
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.establecer_relacion_misma_fase_hijo_revision')
    def AgregarNuevoHijo_Revision(self, proyecto_id, fase_id, item_id, **kw):
        item = DBSession.query(Item).filter_by(coditem=item_id).one()
        fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()#traer items de la fase
        relacionAux = DBSession.query(Relacion).filter_by(coditeminicio=int(item_id)).filter_by(tipo='padre-hijo').all()                                                  
        itemAct = fase.items
        auxItemFase = list()
        hijos = list()
        k = 0
        
        for i in relacionAux:
            hijos.append(i.coditemfin)   
            
        for x in itemAct:
            if not x.coditem in hijos:
                auxItemFase.append(x)
                          
        print "--------------------------------------------------------------"
        for i in itemAct:   
            print i.coditem
        print "--------------------------------------------------------------"

        itemFin=list()
	tipo=0
        return dict(page='Relacion padre-hijo', proyecto_id=proyecto_id, fase_id=fase_id, item=item, itemFin=itemFin, tipo = tipo, itemAct=auxItemFase, value=kw)
    
    @expose('prueba.templates.establecer_relacion_misma_fase_padre_revision')
    def AgregarNuevoPadre_Revision(self, proyecto_id, fase_id, item_id, **kw):
        item = DBSession.query(Item).filter_by(coditem=item_id).one()
        fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()#traer items de la fase
        relacionAux = DBSession.query(Relacion).filter_by(coditemfin=int(item_id)).filter_by(tipo='padre-hijo').all()                                                  
        itemAct = fase.items
        auxItemFase = list()
        padres = list()
        k = 0
        
        for i in relacionAux:
            padres.append(i.coditeminicio)   
            
        for x in itemAct:
            if not x.coditem in padres:
                auxItemFase.append(x)
                          
        print "--------------------------------------------------------------"
        for i in itemAct:   
            print i.coditem
        print "--------------------------------------------------------------"

        itemFin=list()
	tipo=0
        return dict(page='Relacion padre-hijo', proyecto_id=proyecto_id, fase_id=fase_id, item=item, itemFin=itemFin, tipo = tipo, itemAct=auxItemFase, value=kw)

    @expose('')
    def RelacionMismaFase_Revision(self,proyecto_id, fase_id, item_id,**kw):
	if 'itemFin' not in kw:
		redirect("/Modificar_Item_Revision/"+proyecto_id+"/"+fase_id+"/"+item_id)
	calciclo = Ciclos(int(item_id),int(kw['itemFin']))
        ciclo = calciclo.calcular()
        if ciclo == 0:
	    #Actualiza historial de item
	    item=DBSession.query(Item).filter_by(coditem=item_id).one()
	    itemFin=int(kw['itemFin'])
	    itemF=DBSession.query(Item).filter_by(coditem=itemFin).one()
	    self.actualizarHistorialDeItem(item)
	    self.actualizarHistorialDeItem(itemF)
	    #Cambiar estado de item a 'espera'
	    item.estado='desarrollo'
	    item.version=item.version+1
            itemF.version=itemF.version+1
	    DBSession.flush()
	    ##Crea la relacion
            print "no hay cicloooooooo!!!!!!!!!!!!!!!!!!!11***********************"
            
            relacionNueva = Relacion()
            if int(kw['tipo']) == 1:
                relacionNueva.coditeminicio=int(item_id)
                relacionNueva.coditemfin= int(kw['itemFin'])
            else:
                relacionNueva.coditeminicio= int(kw['itemFin'])
                relacionNueva.coditemfin= int(item_id)
            relacionNueva.tipo='padre-hijo'
            DBSession.add(relacionNueva)
	    #Poner en revision items relacionados
	    self.PonerEnRevisionRelacionados(item)
            flash("Relacion establecida exitosamente")
	    redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
        else:
            flash("No se permite la relacion.Un ciclo se formara con ella")   
            redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_padre_revision')
    def EliminarPadre_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	pad = DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item_id).filter_by(tipo='padre-hijo').all()
	padres=list() ##lista de items
	for p in pad:
		aux = DBSession.query(Item).filter_by(coditem=p[0]).one()
		padres.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, padres=padres)

    @expose()
    def eliminarPadre_revision(self, proyecto_id, fase_id, item_id, **kw):
	if 'padre' not in kw:
		redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	padre_id = kw['padre']
	padre=DBSession.query(Item).filter_by(coditem=padre_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(padre)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	padre.version=padre.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=padre_id).filter_by(coditemfin=item_id).filter_by(tipo='padre-hijo').one())
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose('prueba.templates.eliminar_hijo_revision')
    def EliminarHijo_Revision(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	#hallar antecesores actuales
	hij = DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item_id).filter_by(tipo='padre-hijo').all()
	hijos=list() ##lista de items
	for h in hij:
		aux = DBSession.query(Item).filter_by(coditem=h[0]).one()
		hijos.append(aux)
	return dict(page="Eliminar relacion", proyecto_id=proyecto_id, fase_id=fase_id, item=item, hijos=hijos)

    @expose()
    def eliminarHijo_revision(self, proyecto_id, fase_id, item_id, **kw):
	if 'hijo' not in kw:
		redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)
	#Actualiza historial de item
	item=DBSession.query(Item).filter_by(coditem=item_id).one()
	hijo_id = kw['hijo']
	hijo=DBSession.query(Item).filter_by(coditem=hijo_id).one()
	self.actualizarHistorialDeItem(item)
	self.actualizarHistorialDeItem(hijo)
	#Cambiar estado de item a 'espera'
	item.estado='desarrollo'
	item.version=item.version+1
	hijo.version=hijo.version+1
	DBSession.flush()
	#Poner en revision items relacionados
	self.PonerEnRevisionRelacionados(item)
	#Eliminar la relacion
	DBSession.delete(DBSession.query(Relacion).filter_by(coditeminicio=item_id).filter_by(coditemfin=hijo_id).filter_by(tipo='padre-hijo').one())
	redirect("/ConfirmacionModificacion/"+proyecto_id+"/"+fase_id+"/"+item_id)

    @expose()
    def PonerEnRevisionNuevosRelacionados(self, item):
	antecesores=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item.coditem).filter_by(tipo='antecesor-sucesor').all()
	for relacion in antecesores:
		#Verificar si ya esta guardado en la tabla 'revision'
		cont=DBSession.query(Revision).filter_by(inicio=item.coditem).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
		if cont==0:
			i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
			i.estado='revision'
			DBSession.flush()
			#Agregar a la tabla 'revision'
			revision = Revision()
			revision.inicio=item.coditem
			revision.actual=relacion[0]
			revision.anterior=item.coditem
			DBSession.add(revision)
	sucesores=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item.coditem).filter_by(tipo='antecesor-sucesor').all()
	for relacion in sucesores:
		#Verificar si ya esta guardado en la tabla 'revision'
		cont=DBSession.query(Revision).filter_by(inicio=item.coditem).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
		if cont==0:
			i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
			i.estado='revision'
			DBSession.flush()
			#Agregar a la tabla 'revision'
			revision = Revision()
			revision.inicio=item.coditem
			revision.actual=relacion[0]
			revision.anterior=item.coditem
			DBSession.add(revision)
	padres=DBSession.query(Relacion.coditeminicio).filter_by(coditemfin=item.coditem).filter_by(tipo='padre-hijo').all()
	for relacion in padres:
		#Verificar si ya esta guardado en la tabla 'revision'
		cont=DBSession.query(Revision).filter_by(inicio=item.coditem).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
		if cont==0:
			i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
			i.estado='revision'
			DBSession.flush()
			#Agregar a la tabla 'revision'
			revision = Revision()
			revision.inicio=item.coditem
			revision.actual=relacion[0]
			revision.anterior=item.coditem
			DBSession.add(revision)
	hijos=DBSession.query(Relacion.coditemfin).filter_by(coditeminicio=item.coditem).filter_by(tipo='padre-hijo').all()
	for relacion in hijos:
		#Verificar si ya esta guardado en la tabla 'revision'
		cont=DBSession.query(Revision).filter_by(inicio=item.coditem).filter_by(actual=relacion[0]).filter_by(anterior=item.coditem).count()
		if cont==0:
			i=DBSession.query(Item).filter_by(coditem=relacion[0]).one()
			i.estado='revision'
			DBSession.flush()
			#Agregar a la tabla 'revision'
			revision = Revision()
			revision.inicio=item.coditem
			revision.actual=relacion[0]
			revision.anterior=item.coditem
			DBSession.add(revision)

#>>> from sqlalchemy.orm.exc import NoResultFound
#>>> try: 
#...     user = query.filter(User.id == 99).one()
#... except NoResultFound, e:
#...     print e
#No row was found for one()

#>>> from sqlalchemy.orm.exc import MultipleResultsFound
#>>> try: 
#...     user = query.one()
#... except MultipleResultsFound, e:
#...     print e
# Multiple rows were found for one()

    @expose('prueba.templates.importar_tipoitem')
    def ImportarTipoDeItem(self, proyecto_id, fase_id, **kw):
        proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
        fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
        tipos_de_item = DBSession.query(Tipoitem).filter(Tipoitem.codfase != fase_id).filter(Tipoitem.nombre != 'Basico').all() 
        return dict(page='Importacion de tipos de item', proyecto=proyecto, fase=fase, tipos_de_item = tipos_de_item, value=kw)

    @expose()
    #@validate({"nombre": NotEmpty(),}, error_handler=NuevoTipoDeItem)
    def ImportacionTipoDeItem(self, proyecto_id, fase_id, tipo_item_id, **kw):
        tipoitemaux = DBSession.query(Tipoitem).filter_by(codtipoitem = tipo_item_id).first()
        tipoitem = Tipoitem()
        tipoitem.nombre = tipoitemaux.nombre
	tipoitem.codificacion=tipoitemaux.codificacion
	tipoitem.ultimo=0
        tipoitem.codfase = fase_id
        DBSession.add(tipoitem)
        tipoitemaux = DBSession.query(Tipoitem).filter(Tipoitem.nombre == tipoitem.nombre).filter(Tipoitem.codfase == fase_id).filter(Tipoitem.codtipoitem != tipo_item_id).first()
        camposaux = DBSession.query(Campo).filter_by(codtipoitem=tipo_item_id).all()
        for campo in camposaux:
            campos = Campo()
            campos.nombre = campo.nombre
            campos.tipo = campo.tipo
            campos.codtipoitem = tipoitemaux.codtipoitem
            DBSession.add(campos)
        flash("El tipo de item fue importado con exito")
        redirect("/TipoDeItem"+ "/" + str(proyecto_id) + "/" + str(fase_id))

    @expose('prueba.templates.archivo_externo_form')
    def NuevoArchivoExterno(self, proyecto_id, fase_id, item_id, **kw):
        """Mostrar formulario para crear un archivo externo."""
        tmpl_context.form = crear_archivo_externo_form
        kw['proyecto_id'] = proyecto_id
        kw['fase_id'] = fase_id
        kw['item_id'] = item_id
        return dict(modelname='Archivo Externo', value=kw)

    @expose()
    def AgregarArchivoExterno(self, **kw):
        adjunto = ArchivoExterno()
        adjunto.coditem = int(kw['item_id'])
        adjunto.descripcion = kw['descripcion']
        adjunto.vinculo = str(kw['vinculo'].filename)
        DBSession.add(adjunto)
        #write the picture file to the public directory
        public_dirname = os.path.join(os.path.abspath(resource_filename('prueba', 'public')))
        movies_dirname = os.path.join(public_dirname, 'Archivos Externos')
        movie_path = os.path.join(movies_dirname, str(adjunto.codarchivo))
        try:
            os.makedirs(movie_path)
        except OSError:
            #ignore if the folder already exists
            pass
        movie_path = os.path.join(movie_path, adjunto.vinculo)
        f = file(movie_path, "w")
        f.write(kw['vinculo'].value)
        f.close()
        flash(_('Archivo Externo almacenado correctamente: /home/marco/Escritorio/tg2env/prueba/prueba/public/Archivos Externos/None' + str(kw['vinculo'].filename)))
        redirect("/ConsultarItem/"+kw['proyecto_id']+"/"+kw['fase_id']+"/"+kw['item_id'])
