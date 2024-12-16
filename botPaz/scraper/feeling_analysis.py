from pysentimiento.preprocessing import preprocess_tweet
from pysentimiento import create_analyzer

# Inicialización global del analizador para evitar inicializaciones repetidas
analyzer = create_analyzer(task="hate_speech", lang="es")

def feeling_analysis(text: str):
    """
    Realiza el análisis de emociones para el texto dado.
    
    Args:
        text (str): Texto en español a analizar.
        
    Returns:
        str: Emoción predominante identificada en el texto.
    """
    predict = analyzer.predict(text)
    return predict
