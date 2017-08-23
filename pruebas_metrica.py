import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import re ,csv

stoplist = stopwords.words('english')

def preprocesamiento(texto):
	nuevo_texto = re.sub(r"http\S+", "", texto)

	nuevo_texto = BeautifulSoup(nuevo_texto).text
	#nuevo_texto = BeautifulSoup(texto.decode('utf-8','ignore')).get_text()
	nuevo_texto = nuevo_texto.lower()

	tknzr = TweetTokenizer(strip_handles=True, reduce_len=True)
	tokens = tknzr.tokenize(nuevo_texto)
	token_sin_stopwords = [ token for token in tokens  if token not in stoplist and len(token) != 1]

	token_sin_stopwords = [ re.sub('([\W_]+)', '', token) for token in token_sin_stopwords ]  

	return token_sin_stopwords

print "Cargando diccionario Emolex...",
folder = "../NRC-Sentiment-Emotion-Lexicons/Lexicons/"
archivo = pd.read_csv(folder+"NRC-Hashtag-Emotion-Lexicon-v0.2/NRC-Hashtag-Emotion-Lexicon-v0.2.txt",sep='\t',header=None)

dicc_Emolex = {}
for indice in range(archivo.shape[0]):
	emocion,palabra,score= archivo.ix[indice]

	if palabra in dicc_Emolex.keys():
		dicc_Emolex[palabra].append([emocion,score])

	else:
		dicc_Emolex[palabra] = [[emocion,score]]
##dicc emoclex creado!
print "cargado!"

def calcular_metrica(tweet,detalle):
	emociones_contrarias = [["sadness","joy"],["disgust","trust"],["anger","fear"],["surprise","anticipation"]]
	score_metrica = {'sadness':0,'disgust':0,'anger':0,'surprise':0}

	tweet_procesado = preprocesamiento(tweet)
	
	score_tweet = {'anticipation':[],'joy':[],'fear':[],'disgust':[],'anger':[],'trust':[],'surprise':[],'sadness':[]}
	existe = False
	for palabra in tweet_procesado: #si no tiene palabras el tweet? (se elimina todo)
		if palabra in dicc_Emolex.keys():
			existe = True
			for emocion,score in dicc_Emolex[palabra]: #elementos guardados en emolex
				if detalle:
					print ">>>La palabra %s en la emocion *%s* tiene un score de %f"%(palabra,emocion,score)
				score_tweet[emocion].append(score)

	#promediar por tweet (metrica)
	if not existe:
		print "La frase ingresada no tiene palabras en el diccionario de Emolex"
		return

	if detalle:
		print "\nScore finales:"
	for emocion1,emocion2 in emociones_contrarias:
		if score_tweet[emocion1] == [] and score_tweet[emocion2] == []:
			metrica = 0.0

		else:#no nan
			if score_tweet[emocion1] == []: #tweet no tiene emocion1
				score_tweet[emocion1] = [0.0]

			if score_tweet[emocion2] == []:
				score_tweet[emocion2] = [0.0]

			#meter lo de la metrica
			delta= np.sum(score_tweet[emocion1]) - np.sum(score_tweet[emocion2])
			if delta >0:
				metrica = delta #promedio o solo suma??
			else:
				metrica = 0.0
		score_metrica[emocion1] = metrica  #cada tweet tiene una metrica

		print ">La emocion %s tiene un score de %f"%(emocion1,score_metrica[emocion1])

if __name__ == "__main__":
	while(True):
		print "-------------------------------------------------------------------"
		mensaje_entrada = raw_input("Ingresar frase: ")
		detalle = raw_input("Detalle?(s/n)")
		print ""
		if detalle == "s":
			detalle =True
			print "Detalle:"
		else:
			detalle = False
		calcular_metrica(mensaje_entrada,detalle)
