import pandas as pd
import numpy as np
from os import walk


from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import re ,csv

#se eliminan stopwords
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
##revisar el preprocesar


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


f = []
folder = "tweets/"
for (dirpath, dirnames, filenames) in walk(folder):
	f.extend(filenames)
	break


csvFile = open('resultados.csv', 'w')
#Use csv writer
csvWriter = csv.writer(csvFile,quoting=csv.QUOTE_NONNUMERIC)
csvWriter.writerow(["screen_name", "sadness score", "disgust score", "anger score", "surprise score", "cantidad tweets"])

emociones_contrarias = [["sadness","joy"],["disgust","trust"],["anger","fear"],["surprise","anticipation"]]

#para cada uusario dentro de la carpeta
for historia_tweets in f: 
	screen_name = historia_tweets[:-4]
	print "para usuario: ",screen_name

	historial = open(folder+historia_tweets)
	historial = pd.read_csv(folder+historia_tweets)
	cantidad_tweets = historial.shape[0]

	score_usuario = {'sadness':[],'disgust':[],'anger':[],'surprise':[]}
	for tweet in historial["text"].values: #por cada tweet
		#ide,fav_count,ret_count, text, created = tweet.split(',')

		tweet_procesado = preprocesamiento(tweet)
		
		score_tweet = {'anticipation':[],'joy':[],'fear':[],'disgust':[],'anger':[],'trust':[],'surprise':[],'sadness':[]}
		for palabra in tweet_procesado: #si no tiene palabras el tweet? (se elimina todo)
			if palabra in dicc_Emolex.keys():
				for emocion,score in dicc_Emolex[palabra]: #elementos guardados en emolex
					score_tweet[emocion].append(score)

		#promediar por tweet (metrica)
		for emocion1,emocion2 in emociones_contrarias:
			if score_tweet[emocion1] == [] and score_tweet[emocion2] == []:
				metrica = 0.0

			else:#no nan
				if score_tweet[emocion1] == []: #tweet no tiene emocion1
					score_tweet[emocion1] = [0.0]

				if score_tweet[emocion2] == []:
					score_tweet[emocion2] = [0.0]

				#meter lo de la metrica
				metrica = np.mean(score_tweet[emocion1]) - np.mean(score_tweet[emocion2]) #promedio o solo suma??

			score_usuario[emocion1].append( metrica )  #cada tweet tiene una metrica

	print score_usuario
	#promediar las emociones de todos los tweet del usuario
	for emocion in score_usuario.keys():
		score_usuario[emocion] = np.mean(score_usuario[emocion])
		print "Para la emocion %s tiene un score de %f"%(emocion,score_usuario[emocion])

	#escribir resultado
	csvWriter.writerow([screen_name, score_usuario["sadness"], score_usuario["disgust"], score_usuario["anger"], score_usuario["surprise"], cantidad_tweets])
csvFile.close()
