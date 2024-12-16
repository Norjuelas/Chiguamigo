import google.generativeai as genai
import random
import logging

# Configurar mensajes predeterminados
messages = {
    1: "🌐🔒 ¡La seguridad en internet es clave! Tecnochigüiros está comprometido con crear soluciones para un ciberespacio más seguro para todos. #Ciberpaz #Hackaton #SeguridadEnInternet",
    2: "🚀👨‍💻 Tecnochigüiros en acción: protegiendo tu privacidad y tus datos mientras navegas. Juntos podemos hacer de la web un lugar más seguro. #Ciberseguridad #Hackaton",
    3: "🛡️✨ ¡La ciberpaz comienza con cada uno de nosotros! En Tecnochigüiros estamos trabajando para fortalecer la seguridad digital. ¡Únete a la causa! #Ciberpaz #Tecnochigüiros",
    4: "🔍🔐 ¿Sabías que la seguridad en línea es vital? Con Tecnochigüiros estamos creando herramientas para mejorar la ciberseguridad. ¡Sé parte del cambio! #Hackaton #SeguridadDigital",
    5: "🖥️💡 ¡El futuro digital es seguro! Tecnochigüiros participa en la hackatón de ciberpaz para garantizar que tu navegación sea protegida. #Ciberseguridad #Hackaton #SeguridadEnInternet"
}

def cargar_api_key(archivo='D:\\Proyectos\\hackatonCiberpaz\\Chiguamigo\\key\\googleKey.txt'):
    with open(archivo, 'r') as f:
        lineas = f.readlines()
        for linea in lineas:
            if linea.startswith('API_KEY'):
                return linea.split('=')[1].strip()


# Configurar logging
logging.basicConfig(level=logging.INFO)

def llm_response(qs: str):
    """Genera una respuesta usando un modelo generativo y devuelve un mensaje en caso de error."""
    try:
        # Cargar la API key
        GOOGLE_API_KEY = cargar_api_key()
        if not GOOGLE_API_KEY:
            raise ValueError("No se pudo cargar la clave de API de Google.")
        
        # Validar la entrada
        if not isinstance(qs, str) or not qs.strip():
            raise ValueError("La pregunta debe ser una cadena no vacía.")
        
        # Configurar el modelo
        promt = (
            "Eres un bot de twitter encargado de promover la paz y la ciberseguridad, "
            "te llamas Chiguibot. Recuerda contestar en menos de 200 caracteres:"
        )
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generar respuesta
        query = f"{promt} {qs}".strip()
        response = model.generate_content(query)
        
        logging.info("Respuesta generada con éxito.")
        return response.text
    
    except Exception as e:
        # Loggear el error
        logging.error(f"Error al generar respuesta: {e}")
        
        # Devolver un mensaje aleatorio del diccionario
        random_message = messages[random.randint(1, 5)]
        logging.info("Devuelto mensaje alternativo debido a un error.")
        return random_message
