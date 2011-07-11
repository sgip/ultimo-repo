# -*- coding: utf-8 -*-
"""Setup the prueba application"""

import logging
from tg import config
from prueba import model

import transaction


def bootstrap(command, conf, vars):
    """Place any commands to setup prueba here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
	u = model.User()
        u.user_name = u'admin'
	u.user_fullname = u'admin'
	u.password = u'admin'
	u.user_telefono = u'admin'
	u.user_direccion = u'admin'
        u.email_address = u'admin@admin.com'
        model.DBSession.add(u)
    
        g = model.Group()
        g.group_name = u'ADMIN'
        g.users.append(u)
        model.DBSession.add(g)

        #g2 = model.Group()
        #g2.group_name = u'RolPorDefecto1'
        #g2.users.append(u)
        #model.DBSession.add(g2)

	p1 = model.Permission()
        p1.permission_name = u'crear_usuario'
	p1.permission_type = u'sistema'
        p1.description = u'Crear un usuario nuevo'

        p2 = model.Permission()
        p2.permission_name = u'crear_rol'
	p2.permission_type = u'sistema'
        p2.description = u'Crear un rol nuevo'

        p3 = model.Permission()
        p3.permission_name = u'crear_proyecto'
	p3.permission_type = u'sistema'
        p3.description = u'Crear un proyecto nuevo'

	p1.groups.append(g)
	p2.groups.append(g)
	p3.groups.append(g)
	
	model.DBSession.add(p1)
	model.DBSession.add(p2)
	model.DBSession.add(p3)
	    
        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'
        

    # <websetup.bootstrap.after.auth>
