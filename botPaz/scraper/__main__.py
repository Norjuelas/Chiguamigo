import os
import sys
import pandas as pd 
from twitter_agent import TwitterAgent
from feeling_analysis import feeling_analysis
from LLM import llm_response
import random


try:
    from dotenv import load_dotenv
    print("Loading .env file")
    load_dotenv(override=True)
    print("Loaded .env file\n")
except Exception as e:
    print(f"Error loading .env file: {e}")
    sys.exit(1)


def initialize_scraper():
    
    """Inicializa el agente de Twitter con las credenciales del entorno."""
    USER_MAIL = os.getenv('USER_MAIL')
    USER_NAME = os.getenv('TWITTER_USERNAME')
    USER_PASSWORD = os.getenv('TWITTER_PASSWORD')

    if USER_NAME is None or USER_PASSWORD is None:
        raise ValueError(
            "Faltan las variables de entorno para el usuario o la contraseña de Twitter. Verifica tu archivo .env."
        )

    scraper = TwitterAgent(
        mail=USER_MAIL,
        username=USER_NAME,
        password=USER_PASSWORD,
    )
    scraper.login()
    return scraper

def scrape_targets(scraper, targets, max_tweets=2):
    """
    Realiza scraping en función de los objetivos proporcionados.
    :param scraper: Instancia de TwitterAgent.
    :param targets: Lista de cuentas, hashtags o queries.
    :param max_tweets: Número máximo de tweets a obtener por objetivo.
    """
    for target in targets:
        print(f"Scrapeando target: {target}")
        scraper.scrape_tweets(
            max_tweets=max_tweets,
            scrape_username=target if target else None,
        )
def ChinguiBot(targetCounts=None, targetHashtags=None, targetQueries=None):
    try:
        scraper = initialize_scraper()

        # Inicializar DataFrames vacíos para tweets principales y respuestas
        df_main = pd.DataFrame()
        df_replies = pd.DataFrame()

        # Función interna para manejar el scraping y acumulación de datos
        def accumulate_data(targets, target_type):
            nonlocal df_main
            for target in targets:
                print(f"Scrapeando {target_type}: {target}")
                try:
                    scraper.scrape_tweets(
                        max_tweets=10,
                        scrape_username=target if target_type == "username" else None,
                        scrape_hashtag=target if target_type == "hashtag" else None,
                        scrape_query=target if target_type == "query" else None
                    )
                    # Obtener los datos en un DataFrame y concatenarlos
                    new_data = scraper.make_pd()
                    if not new_data.empty:
                        # Limpiar "tweet_id:" si está presente
                        if 'tweet_id' in new_data.columns:
                            new_data['tweet_id'] = new_data['tweet_id'].str.replace("tweet_id:", "").str.strip()
                        df_maxin = pd.concat([df_main, new_data], ignore_index=True)
                except Exception as e:
                    print(f"Error al scrapeear {target_type} '{target}': {e}")

        # Realizar scraping para cada tipo de target
        if targetCounts:
            accumulate_data(targetCounts, "username")

        if targetHashtags:
            accumulate_data(targetHashtags, "hashtag")

        if targetQueries:
            accumulate_data(targetQueries, "query")

        # Mostrar resultados de los tweets principales
        print("Tweets principales acumulados:")
        print(df_main.head())

        # Procesar respuestas si hay tweets acumulados
        if not df_main.empty:
            for tweet_id in df_main["Tweet ID"]:
                handle_value = df_main[df_main["Tweet ID"] == tweet_id]["Handle"].iloc[0]
                print(f"Scrapeando respuestas para el tweet ID: {tweet_id}")
                try:
                    # Llama a la función scrape_replys con el ID del tweet
                    replies = scraper.scrape_replys(handle_value,tweet_id)
                    if replies:
                        # Convierte la lista de respuestas a un DataFrame
                        df_replies = pd.concat([df_replies, pd.DataFrame(replies)], ignore_index=True)
                except Exception as e:
                    print(f"Error al scrapeear respuestas para el tweet {tweet_id}: {e}")

            # Guardar las respuestas en un archivo CSV (opcional)
            print("Scraping de respuestas completado.")
            df_replies.to_csv("respuestas_scrapeadas.csv", index=False)
            print("Respuestas guardadas en 'respuestas_scrapeadas.csv'.")
        else:
            print("El DataFrame principal está vacío. No hay tweets para procesar.")

        # Guardar los tweets principales en un archivo CSV
        df_main.to_csv("tweets_principales.csv", index=False)
        print("Datos guardados en 'tweets_principales.csv'.")

        # Iterar sobre los 'tweet_id'
        for tweet_id in df_main["Tweet ID"]:
            text_value = df_main[df_main["Tweet ID"] == tweet_id]["Content"].iloc[0]
            message=llm_response(text_value)
            scraper.reply(tweet_id=tweet_id, message=message)
              
    except KeyboardInterrupt:
        print("\nScript interrumpido por el usuario. Saliendo...")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        # Cerrar el navegador en caso de que el scraper tenga un driver abierto
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.close()

def main():

    return

if __name__ == "__main__":
    # Listas de cuentas, hashtags o queries
    #target_counts = [ "BallenciAlex"]
    #"NoticiasCaracol", "petrogustavo" ,"Ciberpazcolombi", "NoticiasRCN", "RevistaSemana", duolingoespanol
    main(targetCounts=target_counts)
