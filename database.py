import sqlite3

def crear_base_datos():
    conn = sqlite3.connect('monitoreo.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS datos
                      (pc TEXT, timestamp DATETIME, cpu INTEGER, memoria INTEGER, disco INTEGER)''')
    conn.commit()
    conn.close()

def guardar_datos(pc, cpu, memoria, disco):
    conn = sqlite3.connect('monitoreo.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO datos (pc, timestamp, cpu, memoria, disco) VALUES (?, datetime('now'), ?, ?, ?)",
                   (pc, cpu, memoria, disco))
    conn.commit()
    conn.close()

# Crear la base de datos al inicio
crear_base_datos()
