import google.generativeai as genai

def cargar_api_key(archivo='D:\\Proyectos\\hackatonCiberpaz\\Chiguamigo\\key\\googleKey.txt'):
    with open(archivo, 'r') as f:
        lineas = f.readlines()
        for linea in lineas:
            if linea.startswith('API_KEY'):
                return linea.split('=')[1].strip()


def llm_response(qs:str):
    GOOGLE_API_KEY=cargar_api_key()

    genai.configure(api_key=GOOGLE_API_KEY)
    model=genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(qs)
    
    return response.text

print(llm_response("Hola"))
