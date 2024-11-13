import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi.rfc1902 import *
import sqlite3
from datetime import datetime

# Crear o conectar a la base de datos y la tabla
def init_db():
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS memoria (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        memoria_total REAL,
                        memoria_usada REAL,
                        memoria_libre REAL,
                        host TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cpu (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        cpu_load REAL,
                        host TEXT)''')
    conn.commit()
    conn.close()

async def snmp_walk(target, oid, community='public', port=161):
    results = []
    transportTarget = await UdpTransportTarget.create((target, port))
    
    iterator = walk_cmd(
        SnmpEngine(),
        CommunityData(community),
        transportTarget,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )
    
    async for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print(f'{errorStatus.prettyPrint()} at {errorIndex} on {oid}')
            break
        else:
            for varBind in varBinds:
                results.append(varBind)
                
    return results

def calc_memory(value, hrStorageAllocationUnits):
    return value * hrStorageAllocationUnits / (1024**2)

async def get_ram_memory(host='localhost', comunidad='public'):
    storage_results = await snmp_walk(host, '1.3.6.1.2.1.25.2.3.1', comunidad)
    
    memoria_total = 0
    memoria_usada = 0
    hrStorageAllocationUnits = 0
    memoria_libre = 0
    index = 0
    
    for oid, value in storage_results:
        oid_str = oid.prettyPrint()
        if oid_str.startswith('SNMPv2-SMI::mib-2.25.2.3.1.1.'):
            index += 1
        elif oid_str == 'SNMPv2-SMI::mib-2.25.2.3.1.5.' + str(index):
            memoria_total = int(value.prettyPrint())
        elif oid_str == 'SNMPv2-SMI::mib-2.25.2.3.1.6.' + str(index):
            memoria_usada = int(value.prettyPrint())
        elif oid_str == 'SNMPv2-SMI::mib-2.25.2.3.1.4.' + str(index):
            hrStorageAllocationUnits = int(value.prettyPrint())
    
    if hrStorageAllocationUnits:
        memoria_total = calc_memory(memoria_total, hrStorageAllocationUnits)
        memoria_usada = calc_memory(memoria_usada, hrStorageAllocationUnits)
        memoria_libre = memoria_total - memoria_usada

    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO memoria (host, memoria_total, memoria_usada, memoria_libre) VALUES (?, ?, ?, ?)',
                   (host, memoria_total, memoria_usada, memoria_libre))
    conn.commit()
    conn.close()

    return {
        'Memoria Total (MB)': memoria_total,
        'Memoria Usada (MB)': memoria_usada,
        'Memoria Libre (MB)': memoria_libre,
    }
    
async def get_cpu_load(target, community='public', port=161):
    cpu_load_oid = '1.3.6.1.2.1.25.3.3.1.2'
    cpu_load_results = await snmp_walk(target, cpu_load_oid, community, port)
    
    total_load = 0
    count = 0
    for oid, value in cpu_load_results:
        total_load += int(value.prettyPrint())
        count += 1
    
    avg_cpu_load = total_load / count if count > 0 else 0
    
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cpu (host, cpu_load) VALUES (?, ?)', (target, avg_cpu_load))
    conn.commit()
    conn.close()

    return {
        'Total CPU Load': total_load,
        'Average CPU Load': avg_cpu_load
    }
