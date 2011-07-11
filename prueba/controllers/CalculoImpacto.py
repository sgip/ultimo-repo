from collections import deque
from prueba.model import DBSession
from prueba.model.modelos import Item, Relacion
import pydot

class CalculoImpacto():
    def __init__(self,codItem):
        self.codItem= codItem
        self.cola = deque()
        self.cola.append(self.codItem)
        self.hash = {}
        self.itemsImplicados = list()
        self.codFasesImplicadas = list()
        self.grafo= pydot.Dot(graph_type='digraph') 
	self.codFasesImplicadas;
        
    def calcular(self):
	self.codFasesImplicadas = list()
        self.hash[self.codItem]=self.codItem
        listaItemInicio = list()
        listaItemFin= list()
	aristaX = list()
	aristaY = list()
	indices = list()
        aux = list()
        impacto = 0
        ban=1
        
        while(self.cola):
            coditemActual = self.cola.popleft()
            itemNuevo =  DBSession.query(Item).filter_by(coditem=coditemActual).one()
            self.itemsImplicados.append(itemNuevo)
            
            nombreNodo = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
            # itemOrigen = pydot.Node(nombreNodo, style="filled", fillcolor="red")
            if ban == 1:
		nombreNodoOrigen = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
		itemOrigen = pydot.Node(nombreNodoOrigen, style="filled", fillcolor="red")
                self.grafo.add_node(itemOrigen)
                ban = 0
          
            if not itemNuevo.codfase in self.codFasesImplicadas:
                self.codFasesImplicadas.append(itemNuevo.codfase)
                
            print "calculando....................." + str(coditemActual) + " =========== " + str(itemNuevo.complejidad)
            impacto = impacto + itemNuevo.complejidad
            
            listaItemInicio = DBSession.query(Relacion).filter_by(coditeminicio=itemNuevo.coditem).all()
            for x in listaItemInicio:
                if not self.hash.has_key(x.coditemfin):
                    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditemfin).one()
                    nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
                    self.grafo.add_node(itemDestino)
                    enlace = pydot.Edge(nombreNodo, nombreNodoDestino)

                    self.grafo.add_edge(enlace) 
                    aristaX.append(coditemActual)
		    aristaY.append(x.coditemfin)
		    
                    self.cola.append(x.coditemfin)
                    self.hash[x.coditemfin]=x.coditemfin
		else:
	            pos = 0
	    	    tiene = 0
		    for y in aristaX:
			print "origen ===== " + str(y) + "  destino===== " + str(aristaY[pos])
	            	if y==coditemActual and aristaY[pos]==x.coditemfin:
		        	tiene = 1	
				break
			pos = pos + 1

		    if(tiene == 0):
			    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditemfin).one()
		            nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)   
	                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
		            self.grafo.add_node(itemDestino)
		            enlace = pydot.Edge(nombreNodo, nombreNodoDestino)
		            self.grafo.add_edge(enlace) 
		            aristaX.append(coditemActual)
             		    aristaY.append(x.coditemfin)   
			    
            
            listaItemFin = DBSession.query(Relacion).filter_by(coditemfin=itemNuevo.coditem).all()
            for x in listaItemFin:
                if not self.hash.has_key(x.coditeminicio):
                    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditeminicio).one()
                    nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
                    self.grafo.add_node(itemDestino)
                    enlace = pydot.Edge(nombreNodoDestino,nombreNodo)
                    self.grafo.add_edge(enlace)    
             	    aristaX.append(x.coditeminicio)
      		    aristaY.append(coditemActual) 
                    self.cola.append(x.coditeminicio)
                    self.hash[x.coditeminicio]=x.coditeminicio
		else:
		    pos = 0
	            tiene = 0
		    for y in aristaX:
			print "destino ===== " + str(y) + "  origen ===== " + str(aristaY[pos])
	            	if y==x.coditemfin and aristaY[pos]==coditemActual:
		        	tiene = 1	
				break
			pos = pos + 1
		    if(tiene == 1):
     			    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditeminicio).one()
		            nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
		            itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
		            self.grafo.add_node(itemDestino)
		            enlace = pydot.Edge(nombreNodoDestino,nombreNodo)
		            self.grafo.add_edge(enlace)
                            aristaX.append(x.coditeminicio)
      	            	    aristaY.append(coditemActual)         
          
        self.grafo.write_png("/home/osmar/Escritorio/presentacion/prueba/prueba/public/impacto/imagen.png")
        #self.graficar()
        return (impacto )
        
    def itemPorFaseImplicada(self):
        self.codFasesImplicadas.sort()
        aux = self.codFasesImplicadas[0]
        diccionarioListas={}
        items = list()
        for j in self.codFasesImplicadas:
            aux = j
            print "******************** FAse " + str(aux) + " ******************"
            for i in self.itemsImplicados:
                if i.codfase == j:
                    items.append(i)
                    print i.coditem
            print "-------------fin de la lista en " + str(aux) + " ---------------- "
            
            #if items.__len__() != 0:       
            diccionarioListas[aux]=items
            
            items = list()
        for i in self.itemsImplicados:
		print "Esta implicado" + str(i.coditem)           
                
        return diccionarioListas
	
    def graficar(self):
	c = 0
	implicados = list()
	print "pydot-------_",self.itemsImplicados[0].coditem
	implicados.append(self.itemsImplicados[0].coditem)
	while(implicados):
		print "pydot-------_"
		coditemActual = implicados.popleft()
                itemNuevo =  DBSession.query(Item).filter_by(coditem=coditemActual).one()
		nombreNodo = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)
		if c == 0:
	                itemOri = pydot.Node(nombreNodo, style="filled", fillcolor="red")
			c = 1
		else:
			itemOri = pydot.Node(nombreNodo, style="filled", fillcolor="blue")
		self.grafo.add_node(itemOri)
		padres = DBSession.query(Relacion).filter_by(coditemfin=itemNuevo.coditem).all()
		for padre in padres:
			print "padres" + str(padre.coditeminicio) 
			implicados.append(padre.coditeminicio)
			itemOrigen =  DBSession.query(Item).filter_by(coditem=padre.coditeminicio).one()
			nombreNodoOrigen = itemOrigen.nombre + "   " +itemOrigen.fase.nombre + "   " + str(itemOrigen.complejidad)  
			itemOrigen = pydot.Node(nombreNodoOrigen, style="filled", fillcolor="blue")
			self.grafo.add_node(itemOrigen)
			enlace = pydot.Edge(nombreNodoOrigen,nombreNodo)
			self.grafo.add_edge(enlace) 
		hijos = DBSession.query(Relacion).filter_by(coditeminicio=itemNuevo.coditem).all()
		for hijo in hijos:
			print "hijos" + str(hijo.coditemfin)
   			implicados.append(padre.coditemfin)
			itemDestino =  DBSession.query(Item).filter_by(coditem=hijo.coditemfin).one()
			nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
			itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
			self.grafo.add_node(itemDestino)
			enlace = pydot.Edge(nombreNodo,nombreNodoDestino)
			self.grafo.add_edge(enlace) 
	
	self.grafo.write_png("/home/osmar/Escritorio/presentacion/prueba/prueba/public/impacto/imagen.png")

    def calculoAtras(self):
	self.hash[self.codItem]=self.codItem
        listaItemInicio = list()
        listaItemFin= list()
        aux = list()
        impacto = 0
        ban=1
        aristaX = list()
	aristaY = list()

        while(self.cola):
            coditemActual = self.cola.popleft()
            itemNuevo =  DBSession.query(Item).filter_by(coditem=coditemActual).one()
            self.itemsImplicados.append(itemNuevo)
            
            nombreNodo = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
            # itemOrigen = pydot.Node(nombreNodo, style="filled", fillcolor="red")
            if ban == 1:
		nombreNodoOrigen = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
		itemOrigen = pydot.Node(nombreNodoOrigen, style="filled", fillcolor="red")
                self.grafo.add_node(itemOrigen)
                ban = 0
            
            if not itemNuevo.codfase in self.codFasesImplicadas:
                self.codFasesImplicadas.append(itemNuevo.codfase)
                
            print "calculando....................." + str(coditemActual) + " =========== " + str(itemNuevo.complejidad)
            impacto = impacto + itemNuevo.complejidad
            
            listaItemInicio = DBSession.query(Relacion).filter_by(coditemfin=itemNuevo.coditem).all()
            for x in listaItemInicio:
                if not self.hash.has_key(x.coditeminicio):
                    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditeminicio).one()
                    nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
                    self.grafo.add_node(itemDestino)
                    enlace = pydot.Edge(nombreNodoDestino,nombreNodo)

                    self.grafo.add_edge(enlace) 
                    aristaX.append(x.coditemfin)
		    aristaY.append(coditemActual)
		    
                    self.cola.append(x.coditeminicio)
                    self.hash[x.coditemfin]=x.coditeminicio
		else:
	            pos = 0
	    	    tiene = 0
		    for y in aristaX:
			print "origen ===== " + str(y) + "  destino===== " + str(aristaY[pos])
	            	if y==x.coditemfin and aristaY[pos]==coditemActual:
		        	tiene = 1	
				break
			pos = pos + 1

		    if(tiene == 0):
			    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditeminicio).one()
		            nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)   
	                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
		            self.grafo.add_node(itemDestino)
		            enlace = pydot.Edge(nombreNodoDestino,nombreNodo)
		            self.grafo.add_edge(enlace) 
		            aristaX.append(x.coditemfin)
             		    aristaY.append(coditemActual)
     
        self.grafo.write_png("/home/osmar/Escritorio/presentacion/prueba/prueba/public/impacto/imagen.png")
        
        return (impacto )             

    """Realiza el calculo de impacto teniendo en cuenta solo los items hijos o sucesores solamente"""  	
    def calculoAdelante(self):
        self.hash[self.codItem]=self.codItem
        listaItemInicio = list()
        listaItemFin= list()
        aux = list()
        impacto = 0
        ban=1
        aristaX = list()
	aristaY = list()

        while(self.cola):
            coditemActual = self.cola.popleft()
            itemNuevo =  DBSession.query(Item).filter_by(coditem=coditemActual).one()
            self.itemsImplicados.append(itemNuevo)
            
            nombreNodo = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
            # itemOrigen = pydot.Node(nombreNodo, style="filled", fillcolor="red")
            if ban == 1:
		nombreNodoOrigen = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
		itemOrigen = pydot.Node(nombreNodoOrigen, style="filled", fillcolor="red")
                self.grafo.add_node(itemOrigen)
                ban = 0
            
            if not itemNuevo.codfase in self.codFasesImplicadas:
                self.codFasesImplicadas.append(itemNuevo.codfase)
                
            print "calculando....................." + str(coditemActual) + " =========== " + str(itemNuevo.complejidad)
            impacto = impacto + itemNuevo.complejidad
            
            listaItemInicio = DBSession.query(Relacion).filter_by(coditeminicio=itemNuevo.coditem).all()
            for x in listaItemInicio:
                if not self.hash.has_key(x.coditemfin):
                    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditemfin).one()
                    nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
                    self.grafo.add_node(itemDestino)
                    enlace = pydot.Edge(nombreNodo, nombreNodoDestino)

                    self.grafo.add_edge(enlace) 
                    aristaX.append(coditemActual)
		    aristaY.append(x.coditemfin)
		    
                    self.cola.append(x.coditemfin)
                    self.hash[x.coditemfin]=x.coditemfin
		else:
	            pos = 0
	    	    tiene = 0
		    for y in aristaX:
			print "origen ===== " + str(y) + "  destino===== " + str(aristaY[pos])
	            	if y==coditemActual and aristaY[pos]==x.coditemfin:
		        	tiene = 1	
				break
			pos = pos + 1

		    if(tiene == 0):
			    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditemfin).one()
		            nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)   
	                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
		            self.grafo.add_node(itemDestino)
		            enlace = pydot.Edge(nombreNodo, nombreNodoDestino)
		            self.grafo.add_edge(enlace) 
		            aristaX.append(coditemActual)
             		    aristaY.append(x.coditemfin)
     
        self.grafo.write_png("/home/osmar/Escritorio/presentacion/prueba/prueba/public/impacto/imagen.png")
        
        return (impacto )      
    
