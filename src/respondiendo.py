import tweepy   #(La base principal de bots de twitter en python)
import time    #(Para programar tiempos y poner pausas)
import random   #(Por si necesitas elegir algo de forma random)
#import schedule  #(Para programar tareas cada cierto tiempo)


# Credentials

client = tweepy.Client(bearer_token)
client1 = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_KEY,
    access_token_secret=ACCESS_SECRET
)

def buscaruser():
    users = client.get_users(usernames=['CiberPaz'])
    for user in users:
    	print(user)

user_id = '1585054351843885057'
user_id_cuenta = '599480425'

# Definimos la función de reacción a la cuenta
def tweets_cuenta():
    #Lo primero siempre es buscar los tweets sobre los que vas a trabajar
    #con la linea de abajo obtienes los ultimos 5 tweets de la cuenta que reaccionaras
    tweets = client.get_users_tweets(id=user_id_cuenta,max_results=20)
    #Básicamente para cada tweet que consiga, vamos a buscar si tiene la palabra clave
    #Luego vamos a darle like y Retweet a cada tweet o retweet que cumpla con la especificacion	
    for tweet in tweets.data:
        if '#HackathonCiberPaz' in tweet.text:
            print('Hola!, pronto sabran mas de nuestro proyecto, @tecnochiguiros') #(Para saber si hará la accion o no)
            client1.like(tweet.id) #(Para dar like al tweet)
            
#Definimos los procesos que va a correr
def main():
    tweets_cuenta()
#Con esto evitamos errores por si importan el código, es una costumbre en Python
if __name__ == "__main__":
    main()         