import sqlite3

def crear_base_datos():
    conn = sqlite3.connect('monitoreo.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS datos
                      (pc TEXT, timestamp DATETIME, cpu INTEGER, memoria INTEGER, disco INTEGER)''')
    conn.commit()
    conn.close()

# Ejecuta la función para crear la base de datos y la tabla
crear_base_datos()