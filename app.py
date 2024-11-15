from flask import Flask, jsonify, render_template, request
import logging
from monitor_snmp import get_ram_memory, get_cpu_load, init_db
import asyncio
import sqlite3
import threading

app = Flask(__name__)

# Configurar el nivel de logging para suprimir las peticiones GET
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Inicializar la base de datos
init_db()

# Variables para controlar el monitoreo
monitoring_status = {
    'localhost': True,
    '192.168.1.3': True
}

# Función asincrónica para ejecutar el monitoreo cada 5 minutos
async def monitor_system_resources(host):
    while True:
        if monitoring_status[host]:
            await get_ram_memory(host=host)
            await get_cpu_load(target=host)
        await asyncio.sleep(300)

# Función para ejecutar el monitoreo en un hilo separado para que no interfiera con Flask
def run_async_loop(host):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_system_resources(host))

# Iniciar el monitoreo en hilos independientes al iniciar la aplicación
thread_local = threading.Thread(target=run_async_loop, args=('localhost',))
thread_local.daemon = True
thread_local.start()

thread_remote = threading.Thread(target=run_async_loop, args=('192.168.1.3',))
thread_remote.daemon = True
thread_remote.start()

@app.route('/pause/<host>')
def pause_monitoring(host):
    monitoring_status[host] = False
    return jsonify({'status': 'paused'})

@app.route('/resume/<host>')
def resume_monitoring(host):
    monitoring_status[host] = True
    return jsonify({'status': 'resumed'})

@app.route('/status/<host>')
def get_status(host):
    return jsonify({'status': 'running' if monitoring_status[host] else 'paused'})

@app.route('/first-record-date/<host>')
def first_record_date(host):
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(timestamp) FROM memoria WHERE host=? UNION SELECT MIN(timestamp) FROM cpu WHERE host=?", (host, host))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        return jsonify({'first_record_date': row[0]})
    else:
        return jsonify({'first_record_date': None})

@app.route('/memoria/<host>')
def memoria(host):
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memoria WHERE host=? ORDER BY timestamp DESC LIMIT 1", (host,))
    row = cursor.fetchone()
    conn.close()

    if (row):
        memoria_data = {
            'Memoria Total (MB)': row[3],
            'Memoria Usada (MB)': row[4],
            'Memoria Libre (MB)': row[5],
            'Timestamp': row[2]
        }
    else:
        memoria_data = {}

    return jsonify(memoria_data)

@app.route('/memoria-historico/<host>')
def memory_history(host):
    start_date = request.args.get('start')
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    if start_date:
        cursor.execute("SELECT timestamp, memoria_total, memoria_usada, memoria_libre FROM memoria WHERE host=? AND timestamp >= ? ORDER BY timestamp ASC", (host, start_date))
    else:
        cursor.execute("SELECT timestamp, memoria_total, memoria_usada, memoria_libre FROM memoria WHERE host=? ORDER BY timestamp DESC LIMIT 100", (host,))
    rows = cursor.fetchall()
    conn.close()

    historico_data = [{'timestamp': row[0], 'total': row[1], 'usada': row[2], 'libre': row[3]} for row in rows]
    historico_data.reverse()  # Reverse to show the most recent data first

    return jsonify(historico_data)

@app.route('/cpu/<host>')
def cpu(host):
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cpu WHERE host=? ORDER BY timestamp DESC LIMIT 1", (host,))
    row = cursor.fetchone()
    conn.close()

    if row:
        cpu_data = {
            'CPU Load (%)': row[2],
            'Timestamp': row[1]
        }
    else:
        cpu_data = {}

    return jsonify(cpu_data)

@app.route('/cpu-historico/<host>')
def cpu_historico(host):
    start_date = request.args.get('start')
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    if start_date:
        cursor.execute("SELECT timestamp, cpu_load FROM cpu WHERE host=? AND timestamp >= ? ORDER BY timestamp ASC", (host, start_date))
    else:
        cursor.execute("SELECT timestamp, cpu_load FROM cpu WHERE host=? ORDER BY timestamp DESC LIMIT 100", (host,))
    rows = cursor.fetchall()
    conn.close()

    historico_data = [{'timestamp': row[0], 'cpu_load': row[1]} for row in rows]
    historico_data.reverse()  # Reverse to show the most recent data first

    return jsonify(historico_data)

@app.route('/grafico')
def grafico():
    host = request.args.get('host', 'localhost')
    return render_template('grafico.html', host=host)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
