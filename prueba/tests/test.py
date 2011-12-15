import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from prueba import *
from collections import deque
from prueba.model.modelos import  Item,Fase,Relacion

class utilTestCase(unittest.TestCase):

	def setUp(self):
		db = create_engine('postgresql://test:test@localhost:5432/prueba')
		Session = sessionmaker(bind=db)
		self.session = Session()
		self.items = self.session.query(Item).filter_by(codfase=2).all()
		self.item = None
		
	def runTest(self):
		self.poderGenerarLB()
		self.tieneAntecesor()

	def poderGenerarLB(self):
		"""Para generara una linea base, todo los items en la fase deben estar aprobados"""
		
		cantItems = 0
		for i in self.items:
			cantItems = cantItems + 1
		aprobados = 0
		for i in self.items:
			if i.estado == 'aprobado':
				aprobados = aprobados + 1
			
		assert cantItems != aprobados, 'Se puede generar una linea base cuando todos los items de la fase esta estan aprobados'
		
	def tieneAntecesor(self):
		"""Saber si un item tiene algun ancentro, sea indirecto o no"""
		self.item = self.session.query(Item).filter_by(coditem=10).first()
		itemFase = self.item.fase.items 
		faseItemAnt = int(self.item.fase.codfase) - 1
		antecesores = self.session.query(Relacion).filter_by(coditemfin=10).filter_by(tipo='antecesor-sucesor').all()
		
		faseAnt = self.session.query(Fase).filter_by(codfase=faseItemAnt).first()
		itemFaseAnt = self.session.query(Item).filter_by(fase=faseAnt).all()
		
		itemFaseAnterior = list()
		pila = list()
		  
		for h in itemFaseAnt:
		    itemFaseAnterior.append(h.coditem)
		    
		for j in antecesores:
		    if j.coditeminicio in itemFaseAnterior:
		        valor = 1
		        break  
		
		padres = self.session.query(Relacion).filter_by(coditemfin=10).filter_by(tipo='padre-hijo').all()
		for i in padres:
		    pila.append(i.coditeminicio)  
		
		valor = 0
		  
		while(pila and valor!=1):
		    x = pila.pop()
		    antecesores = self.session.query(Relacion).filter_by(coditemfin=x).filter_by(tipo='antecesor-sucesor').all()
		    cantidad=0
		    for m in antecesores:
		        cantidad = cantidad + 1
		        m.coditeminicio
		    
		    if cantidad == 0:
		        antecesores = self.session.query(Relacion).filter_by(coditemfin=x).filter_by(tipo='padre-hijo').all()
		        for i in antecesores:   
		            pila.append(i.coditeminicio)
		    else:
		        for j in antecesores:
		            if j.coditeminicio in itemFaseAnterior:
		                valor = 1
		                break
		               
		assert valor != 1, 'El item no tiene antecesores'		
	
		
		
	
if __name__ == "__main__":
	unittest.main()

	
