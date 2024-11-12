# app.py
from flask import Flask, jsonify, render_template
from monitor_snmp import obtener_memoria_ram
import asyncio

app = Flask(__name__)

@app.route('/memoria')
async def memoria():
    datos_memoria = await obtener_memoria_ram()  # Llama a obtener_memoria_ram
    return jsonify(datos_memoria)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
