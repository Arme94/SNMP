from flask import Flask, jsonify, render_template
from monitor_snmp import obtener_datos_snmp
import asyncio

app = Flask(__name__)

async def obtener_datos():
    # OID específico de Windows para monitorear la memoria total
    memoria_total = await obtener_datos_snmp(oid='1.3.6.1.2.1.25.3.3.1.2')
    
    # Extraer el valor de la memoria total del diccionario
    memoria_total_valor = list(memoria_total.values())[0] if memoria_total else None
    
    return {
        'Memoria Total': memoria_total_valor
    }

@app.route('/memoria')
async def memoria():  # Cambia a función asíncrona
    datos = await obtener_datos()  # Asegúrate de usar await aquí
    return jsonify(datos)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)