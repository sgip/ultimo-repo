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
        
    def calcular(self):
        self.hash[self.codItem]=self.codItem
        listaItemInicio = list()
        listaItemFin= list()
        aux = list()
        impacto = 0
        ban=1
        
        while(self.cola):
            coditemActual = self.cola.popleft()
            itemNuevo =  DBSession.query(Item).filter_by(coditem=coditemActual).one()
            self.itemsImplicados.append(itemNuevo)
            
            nombreNodo = itemNuevo.nombre + "   " +itemNuevo.fase.nombre + "   " + str(itemNuevo.complejidad)  
            itemOrigen = pydot.Node(nombreNodo, style="filled", fillcolor="red")
            if ban == 1:
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
                                
                    self.cola.append(x.coditemfin)
                    self.hash[x.coditemfin]=x.coditemfin
            
            listaItemFin = DBSession.query(Relacion).filter_by(coditemfin=itemNuevo.coditem).all()
            for x in listaItemFin:
                if not self.hash.has_key(x.coditeminicio):
                    itemDestino =  DBSession.query(Item).filter_by(coditem=x.coditeminicio).one()
                    nombreNodoDestino = itemDestino.nombre + "   " +itemDestino.fase.nombre + "   " + str(itemDestino.complejidad)  
                    itemDestino = pydot.Node(nombreNodoDestino, style="filled", fillcolor="blue")
                    self.grafo.add_node(itemDestino)
                    enlace = pydot.Edge(nombreNodoDestino,nombreNodo)
                    self.grafo.add_edge(enlace)
                    
                    self.cola.append(x.coditeminicio)
                    self.hash[x.coditeminicio]=x.coditeminicio
          
        #    for coditem in aux:
        #        self.cola.append(coditem)
        #        self.hash[coditem]=coditem
        self.grafo.write_png("/home/lilian/tg2env/prueba/prueba/public/impacto/nombre.png")
        
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
                   
                
        return diccionarioListas
      
      	
    
