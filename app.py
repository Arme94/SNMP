from flask import Flask, jsonify, render_template
from monitor_snmp import obtener_memoria_ram, init_db
import asyncio
import sqlite3
import threading

app = Flask(__name__)

# Inicializar la base de datos
init_db()

# Función asincrónica para ejecutar el monitoreo cada 3 segundos
async def monitorizar_memoria():
    while True:
        await obtener_memoria_ram()
        await asyncio.sleep(5)

# Función para ejecutar el monitoreo en un hilo separado para que no interfiera con Flask
def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitorizar_memoria())

# Iniciar el monitoreo en un hilo independiente al iniciar la aplicación
thread = threading.Thread(target=run_async_loop)
thread.daemon = True  # Para que el hilo se cierre cuando la aplicación se cierre
thread.start()

@app.route('/memoria')
def memoria():
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memoria ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        memoria_data = {
            'Memoria Total (MB)': row[2],
            'Memoria Usada (MB)': row[3],
            'Memoria Libre (MB)': row[4],
            'Timestamp': row[1]
        }
    else:
        memoria_data = {}

    return jsonify(memoria_data)

@app.route('/memoria-historico')
def memoria_historico():
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, memoria_total, memoria_usada, memoria_libre FROM memoria ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    conn.close()

    historico_data = [{'timestamp': row[0], 'total': row[1], 'usada': row[2], 'libre': row[3]} for row in rows]

    return jsonify(historico_data)

@app.route('/grafico')
def grafico():
    return render_template('grafico.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
