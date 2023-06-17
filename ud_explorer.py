# -*- coding: utf-8 -*-
#Copyright 2023 P. Milizia CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
#La presente versione presuppone che sia installato il modulo sympy (se si dispone di pip, digitare "pip3 install sympy" o "pip install sympy" secondo la configurazione del sistema)
 
import re
import glob
from sympy import symbols
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC, SID = symbols('ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC SID')
 
 
#CLASSE PYTHON PER LA LETTURA DI UN TREEBANK UD
class UD:
	def __init__(self, dir_name: str = '.'):
		#legge i file
		files=glob.glob(dir_name+'/*conllu')
		data=''
		for filepath in files:
			with open(filepath, 'r') as file:
				data+=file.read()
 
		#ordina i file e crea una variabile text_list con l'elenco dei testi
		data=data.split('# newdoc ')[1:]
		data.sort()
		data='# newdoc '+'# newdoc '.join(data)
		self.text_list=re.findall('#\snewdoc\s.*', data)
 
		#crea le variabili fondamentali
		self.data=self.add_sent_id(data)
		self.tokens=self.create_tokens(self.data)
		self.sentences=self.create_sentences(self.tokens)
 
	#aggiunge il campo sent_id
	def add_sent_id(self, text):
		sid_expr=re.compile('(?<=sent_id\s=\s).*')
		text=re.split('\n',text)
		output=''
		sid=''
		for line in text:
			found=re.search(sid_expr,line)
			if found != None:
				sid=found.group()
			if line !='' and line[0] != '#':
				line = line+'\t'+sid
			output += line+'\n'
		return output
 
	#crea la lista dei tokens
	def create_tokens(self, data):
		expr=re.compile('\n([0-9]*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t(.*?)\t([0-9]*?)\t(.*?)\t(.*?)\t(.*?)\t(.*)')
		tokens = re.findall(expr, data)
		for i in range(len(tokens)):
			tokens[i]=list(tokens[i])
			for ii in (5,9):
				tokens[i][ii]=re.split('\|',tokens[i][ii])
			tokens[i][0]=int(tokens[i][0])
			tokens[i][6]=int(tokens[i][6])
		keys = [ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC, SID]
		tokens=[dict(zip(keys, l)) for l in tokens ] 
		return tokens
 
	#crea il dizionario delle frasi
	def create_sentences(self, tokens):
		sentences={}
		sid=''
		for t in tokens:
			if t[SID] != sid:
				sid=t[SID]
				sentences[sid]=['root']
			sentences[sid].append(t)
		return sentences
 
	#funzioni di interrogazione
	def parent_of(self, x):
		return self.sentences[x[SID]][x[HEAD]]
 
	def grandparent_of(self, occurrence):
		return self.parent_of(self.parent_of(occurrence))
 
	def right_of(self, x, n: int = 1):
		try:
			outp=self.sentences[x[SID]][x[ID]+n]
		except IndexError:
			outp=None
		return outp
 
	def left_of(self, x, n: int = 1):
		if x[0]-n > 0:
			outp=self.sentences[x[SID]][x[ID]-n]
		else:
			outp=None
		return outp
 
	def children_of(self,x):
		return [t for t in self.sentences[x[SID]][1:] if self.parent_of(t)==x]
 
	def lineage_of(self, x):
		output = [x]
		while x != 'root':
			y=self.parent_of(x)
			output.append(y)
			x=y
		return output
 
	#funzione per estrarre il testo di una frase
	def get_sentence(self, x):
		return [j[FORM] for j in self.sentences[x][1:]]
 
#funzione per estrarre la posizione di un token
def form_and_position_of(x):
	return (x[FORM],x[SID],x[ID])
 
#ESEMPI DI UTILIZZO
 
#Si assume che i file del treebank di copto siano in una sottocartella denominata 'connlu'
 
treebank=UD('conllu')
 
 
#mostra forma e posizione di tutti i token che figurano in funzione di oggetto diretto di forme del lessema ⲉⲓⲣⲉ
 
for token in treebank.tokens:
	if token[DEPREL] =='obj' and treebank.parent_of(token)[LEMMA]=='ⲉⲓⲣⲉ':
		print(form_and_position_of(token))
 
 
#trova tutte le occorrenze di 'ⲙⲙⲟ' e di 'ⲛ' come marca dell'oggetto diretto
#alle seguenti condizioni:
#1) che la frase sia al passato perfettivo positivo
#2) che almeno un elemento sia interposto tra verbo e preposizione
 
found_tokens=[]
 
def is_past(o):
	answer = False
	for child in treebank.children_of(o):
		if child[FORM]=='ⲁ' and child[UPOS]=='AUX':
			answer = True
			break
	return answer
 
for token in treebank.tokens:
	if (token[FORM] == 'ⲙⲙⲟ' or token[FORM] == 'ⲛ') and token[DEPREL]=='case':
		try:
			regens = treebank.grandparent_of(token)
			noun_pronoun = treebank.parent_of(token)
			if noun_pronoun[DEPREL]=='obj' and is_past(regens) and (token[ID] - regens[ID])>1:
				found_tokens.append(token)
		except:
			pass
 
for o in found_tokens:
	print(o)