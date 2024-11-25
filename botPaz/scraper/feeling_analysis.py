from transformers import AutoTokenizer
from pysentimiento.preprocessing import preprocess_tweet
from pysentimiento import create_analyzer

def feeling_analysis(text: str):
    
    analyzer = create_analyzer(task="emotion", lang="es")

    tokenizer = AutoTokenizer.from_pretrained('pysentimiento/robertuito-base-cased')

    predict = analyzer.predict(text)

    return predict.output

if "__name__" == "__main__":
    print(feeling_analysis("soy muy feliz"))
    #output= AnalyzerOutput(output=joy, probas={joy: 0.990, surprise: 0.003, others: 0.003, disgust: 0.001, fear: 0.001, sadness: 0.001, anger: 0.001})


    """
    def analyze_hate_speech(df, text_column, model="cardiffnlp/twitter-roberta-base-hate"):

        Detecta mensajes de odio en un DataFrame basado en una columna de texto.

    # Cargar un modelo preentrenado para detección de odio
    classifier = pipeline("text-classification", model=model)
    
    def detect_hate(text):
        try:
            result = classifier(text)[0]
            return {"label": result['label'], "score": result['score']}
        except Exception as e:
            return {"label": "ERROR", "score": 0.0}
    
    # Analizar la columna y agregar resultados al DataFrame
    df["hate_analysis"] = df[text_column].apply(detect_hate)
    return df
    """