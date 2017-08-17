import pandas as pd
import numpy as np

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


def leer_resultados():
	aux = pd.read_csv("resultados.csv")
	diccionario = aux.set_index('id').to_dict()
	nuevo_resultados = pd.DataFrame(data=diccionario)#pd.from_dict(diccionario)
	nuevo_resultados = nuevo_resultados[['screen name', 'sadness score', 'disgust score', 'anger score', 'surprise score','cantidad tweets']]

	return nuevo_resultados

def calcular_metrica(tweet):
	emociones_contrarias = [["sadness","joy"],["disgust","trust"],["anger","fear"],["surprise","anticipation"]]
	score_metrica = {'sadness':0,'disgust':0,'anger':0,'surprise':0}

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
			delta= np.sum(score_tweet[emocion1]) - np.sum(score_tweet[emocion2])
			if delta >0:
				metrica = delta #promedio o solo suma??
			else:
				metrica = 0.0
		score_metrica[emocion1] = metrica  #cada tweet tiene una metrica
	return score_metrica


# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json,csv,time, tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

#consumer key, consumer secret, access token, access secret.
ckey="gQ1RX1eqCRS39n1dmL9nVzAEp"
csecret="iMiZA2xXC4o7TsypLHj22HP1R0SAdfYqxYgFDKU33mra2SGhyA"
atoken="320425023-iyx7eywe75Po9VtkaOkhcrlhXGFTwzrYYq55xcoH"
asecret="4GAlKtNyS0Z4SIOdo4DnlFsBl8KlfczOhGy8I4yByF1Tb"

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)

#print aux.head()
class listener(StreamListener):

	def on_data(self, data):
		json_data = json.loads(data)
		#print(json.dumps(json_data,indent=2))
		if json_data["text"][:2] != "RT":
			print "************************************NUEVO TWEET DETECTADO************************************"

			id_user = json_data["user"]["id"]
			print "Id usuario: ",id_user
			print "Nombre usuario: ",json_data["user"]["screen_name"]
			print "id tweet: ",json_data["id"]
			print "Fecha creacion: ",json_data["created_at"]
			print "Text: ",json_data["text"]


			diccionario_resultados = leer_resultados()

			#recalcular metrica
			scores_tweet =  calcular_metrica(json_data["text"])

			#actualizar datos
			cantidad_tweets_actual = diccionario_resultados["cantidad tweets"][id_user]
			print "Las emociones del tweet son: "
			for emocion,score in scores_tweet.iteritems():
				print "%s , score: %f"%(emocion,score)
				nuevo_valor = (diccionario_resultados[emocion+ " score"][id_user]*cantidad_tweets_actual + score) /(cantidad_tweets_actual+1)
				diccionario_resultados[emocion+ " score"][id_user] = nuevo_valor
			
			diccionario_resultados["cantidad tweets"][id_user]+=1

			#notificar

			#guardar
			diccionario_resultados.to_csv('resultados.csv', index=True, index_label= "id")

		return(True)

	def on_error(self, status):
		print sstatus
print "ESCUCHANDO..."
twitterStream = Stream(auth, listener())
##usuarios a streamear
ids = open("diccionario_usuarios.txt")
ids_usuarios = []
for linea in ids:
	id_user = linea.split(" ")[-1].strip()
	ids_usuarios.append(id_user)
twitterStream.filter(follow=ids_usuarios)