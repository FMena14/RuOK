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

	return nuevo_resultados,aux

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
ckey="OfnyLSvIAMbXg31OYl0zggnua"
csecret="BYQeUOSenSVXkWNztD1zALmuGVkLW4vmFIQ68HD5J3Lg04BdNX"
atoken="899659689566273537-T9RkSGXCDe2DdUmzfddaIkHifKwHLjk"
asecret="ZOQWfqd5N9HkOCt81KdHwh1xzkgE7z0IbZcCAZoz4MDB0"

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)

#print aux.head()
class listener(StreamListener):

	def on_data(self, data):
		global ids_usuarios
		json_data = json.loads(data)
		try:
			json_data["text"]
		except:
			#tweet de notificacion (borrar, modificar)
			return

		#print(json.dumps(json_data,indent=2))

		if json_data["text"][:2] != "RT" and str(json_data['user']["id"]) in ids_usuarios:
			print "************************************NUEVO TWEET DETECTADO************************************"

			id_user = json_data["user"]["id"]
			print "Id usuario: ",id_user
			screen_name = json_data["user"]["screen_name"]
			print "Nombre usuario: ",screen_name
			#print "id tweet: ",json_data["id"]
			print "Fecha creacion: ",json_data["created_at"]
			print "Text: ",json_data["text"]


			diccionario_resultados,resultados_df = leer_resultados()

			#recalcular metrica
			scores_tweet =  calcular_metrica(json_data["text"])

			#actualizar datos
			cantidad_tweets_actual = diccionario_resultados["cantidad tweets"][id_user]
			print "Las emociones del tweet son: "
			for emocion,score in scores_tweet.iteritems():
				print "Emocion %s , Score: %f"%(emocion,score)
				viejo_valor = diccionario_resultados[emocion+ " score"][id_user]
				nuevo_valor = (viejo_valor*cantidad_tweets_actual + score) /(cantidad_tweets_actual+1)
				diccionario_resultados[emocion+ " score"][id_user] = nuevo_valor
			

				#valores treshold
				promedio = np.mean(resultados_df[emocion+" score"])
				std = np.std(resultados_df[emocion+" score"])

				#verificando
				#print "VERIFICANDO %s"%(emocion)
				#print "PROMEDIO DEL GRUPO: ",promedio
				#print "STD DEL GRUPO: ",std
				#print "SCORE del tweet: ",score
				#print "NUEVO SCORE PROMEDIO: ",	nuevo_valor

				#notificar
				if nuevo_valor > promedio + 2*std:
					print "----->NOTIFICAR EN BASE AL HISTORIAL DE LA EMOCION %s PARA ESE USUARIO"%(emocion)
					try:
						api.send_direct_message(user=id_user,text="Hi %s,\nEverything is right?, We are seeing your tweets and is seems to like you are a bit %s.\nFor any help you need, please contact us contacto.ruok@gmail.com\n\nRuOK~"%(screen_name,emocion))
					except:
						#no se puede mandar ya que no te siguen
						pass
				"""
				if nuevo_valor > viejo_valor: 
					print "----->NOTIFICAR EN BASE AL TWEET ACTUAL DE LA EMOCION %s"%(emocion)
					try:
						api.send_direct_message(user=id_user,text="Hi %s,\nEverything is right?, We see your last tweet and is seems to like you are a bit %s.\nFor any help you need, please contact us contacto.ruok@gmail.com\n\nRuOK~"%(screen_name,emocion))
					except:
						pass
				"""
			diccionario_resultados["cantidad tweets"][id_user]+=1

			#guardar
			diccionario_resultados.to_csv('resultados.csv', index=True, index_label= "id")

		return(True)

	def on_error(self, status):
		print status
print "ESCUCHANDO..."
twitterStream = Stream(auth, listener())
##usuarios a streamear
ids = open("diccionario_usuarios.txt")
ids_usuarios = []
for linea in ids:
	id_user = linea.split(" ")[-1].strip()
	ids_usuarios.append(id_user)
twitterStream.filter(follow=ids_usuarios)