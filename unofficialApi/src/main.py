from .classes.twitter_client import TwitterClient
import logging


def start():
    """
    Función principal que inicializa el cliente de Twitter y ejecuta las operaciones principales.
    """
    try:
        # Inicializar el cliente de Twitter
        client = TwitterClient()

        # Establecer el cliente e iniciar sesión
        result = client.get_client()  # Sincronizada

        if result:
            logging.info("Cliente de Twitter inicializado exitosamente.")
            # Aquí puedes agregar tus operaciones principales
            # Ejemplo:
            # tweets = client.fetch_tweets("https://twitter.com/some_user", 10)
            # logging.info(f"Tweets obtenidos: {tweets}")
            pass

    except Exception as e:
        logging.error(f"Error durante la ejecución: {str(e)}")


if __name__ == "__main__":
    # Configurar el sistema de logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Ejecutar la función principal
    start()


