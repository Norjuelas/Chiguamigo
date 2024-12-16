from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# Función que maneja el bot de Selenium
def run_selenium_bot(data):
    # Aquí va tu lógica de Selenium
    print(f"Ejecutando el bot con: {data}")
    time.sleep(5)  # Simula el trabajo del bot
    print("Bot finalizado")

@app.route('/start-bot', methods=['POST'])
def start_bot():
    data = request.json  # Recibe datos desde la extensión
    thread = threading.Thread(target=run_selenium_bot, args=(data,))
    thread.start()  # Corre el bot en un hilo separado
    return jsonify({"status": "Bot iniciado"})

if __name__ == '__main__':
    app.run(debug=True)
