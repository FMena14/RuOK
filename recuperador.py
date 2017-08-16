# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json,csv,time, tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

#consumer key, consumer secret, access token, access secret.
ckey="LPG9E2zQHgI9LfYEpffN49u49"
csecret="Q4QSyKGewE4BNQHMyyroGwjdm6888wpDVgdUVwcD5edP8CRbUS"
atoken="877580737125507072-3x6CZ4vMpytPL3TZdv9llzPuaVzprqE"
asecret="0y0uWwNuk9p6vZNrSHwTfoiWQPQp7pgAXMwkaCSdYFcYK"

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)

"""

#searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]

#searched_tweets = api.search(q="trump",result_type= 'mixed',truncated=False, show_user=True,count=10)

searched_tweets = [status for status in tweepy.Cursor(api.search, q="sad", since = "2017-01-01", lang="en",show_user=True).items(1)]
#print(json.dumps(searched_tweets[0]._json, indent=2)) 

#json.dumps(status._json)
#print(json.dumps(searched_tweets[0]._json, indent=2)) 

print "datos rescatados:"
print "Id user:", searched_tweets[0].user.id
print "Nombre:", searched_tweets[0].user.name
print "Screen name;" ,searched_tweets[0].user.screen_name
print "Descripcion:", searched_tweets[0].user.description
print "Location:", searched_tweets[0].user.location
print "Fecha:", searched_tweets[0].created_at
print "Tweet:" ,searched_tweets[0].text

# Open/create a file to append data to
csvFile = open('result.csv', 'a')
#Use csv writer
csvWriter = csv.writer(csvFile,quoting=csv.QUOTE_NONNUMERIC)
csvWriter.writerow(["id user", "name","screen name","description","location","date","tweet"])


query1 = "lonely" or "bipolar" or "crazy" or "suicide" or "end" or "sorry" or "hopelessness" or "sad" or "alone" or "damage" or "give up" or "rage" or "dissapoint"or "mind" or "aggression" or "anger" or "fear" or "cares" or"nobody" or "oppression"or "feel" or "break" or "pornography" or "defrauded" or "fugitive"or "murder" or "heart" or "arrest" or "kill" or "crime" or "death" or "substance"
query2= "weapon" or "pain" or "suicidal" or "depression" or "anxiety" or "mental"or "depressed" or "i hate happy" or "sad today" or "sad day" or "jail" or "so mad"or "cannot live" or "not have love" or "stupid people" or "bad people" or "mad internet" or "hate living here" or "nobody understand"
query = query1 or query2
max_tweets = 10000

date = time.strftime("%Y-%m-%d")
for status in tweepy.Cursor(api.search, q=query, until ="2017-06-23", 
				lang="en",show_user=True, geocode= "35.1466548,-93.626001,700mi").items(max_tweets):
	#valores a guardar
	csvWriter.writerow([status.user.id,
						status.user.name,
						status.user.screen_name,
						status.user.description,
						status.user.location,
						status.created_at,
						status.text.encode('utf-8').strip()])
						#encode('utf-8').strip()])#.encode('utf-8')])
csvFile.close()

""" 


dicc_usuarios = open("diccionario_usuarios.txt","a") 
 
<<<<<<< HEAD
screen_name = "yungjojodeno"
=======
screen_name = "LifeSuckSmith"
>>>>>>> e228c01306ecdb424e8cf767336394c2930b7a18

#for ides in ids:
# formato id usuario
csvFile = open("tweets/"+screen_name+'.csv', 'a')
#Use csv writer
csvWriter = csv.writer(csvFile,quoting=csv.QUOTE_NONNUMERIC)
csvWriter.writerow(["id", "favorite count","retweet count","text","created at"])
max_tweets = 50000

usuario = api.get_user(screen_name = screen_name)
dicc_usuarios.write(screen_name+ " "+usuario.name+ " "+str(usuario.id)+"\n") 
dicc_usuarios.close()

#para rescatar info de usuario
for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items(max_tweets):
	#print(json.dumps(status._json, indent=2)) 
	
	if status.text[:2] != 'RT': #si el tweet lo escribio el
		csvWriter.writerow([status.id,
			status.favorite_count,
			status.retweet_count,
			status.text,
			status.created_at
			])

#API.user_timeline([id/user_id/screen_name][, since_id][, max_id][, count][, page])

csvFile.close()

"""
class listener(StreamListener):

    def on_data(self, data):
        print(data)
        return(True)

    def on_error(self, status):
        print status
#twitterStream = Stream(auth, listener())
#twitterStream.userstream(usuarios)
#twitterStream.filter(track=["car"]) #follow=

"""
