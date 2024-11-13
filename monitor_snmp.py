# monitor_snmp.py
import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi.rfc1902 import *

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
    return value * hrStorageAllocationUnits / (1024**3)

async def obtener_memoria_ram(host='localhost', comunidad='public'):
    storage_results = await snmp_walk(host, '1.3.6.1.2.1.25.2.3.1', comunidad)
    
    memoria_total = 0
    memoria_usada = 0
    hrStorageAllocationUnits = 0
    memoria_libre = 0
    index = 0
    
    for oid, value in storage_results:
        oid_str = oid.prettyPrint()
        if(oid_str.startswith('SNMPv2-SMI::mib-2.25.2.3.1.1.')):
            index += 1
        elif(oid_str == 'SNMPv2-SMI::mib-2.25.2.3.1.5.'+str(index)):
            memoria_total = int(value.prettyPrint())
        elif(oid_str == 'SNMPv2-SMI::mib-2.25.2.3.1.6.'+str(index)):
            memoria_usada = int(value.prettyPrint())
        elif(oid_str == 'SNMPv2-SMI::mib-2.25.2.3.1.4.'+str(index)):
            hrStorageAllocationUnits = int(value.prettyPrint())
        else:
            continue
            
    if hrStorageAllocationUnits:
        memoria_total = calc_memory(memoria_total, hrStorageAllocationUnits)
        memoria_usada = calc_memory(memoria_usada, hrStorageAllocationUnits)
        memoria_libre = memoria_total - memoria_usada
        
    print(f'Memoria Total: {memoria_total} MB')
    print(f'Memoria Usada: {memoria_usada} MB')
    print(f'Memoria Libre: {memoria_libre} MB')

    return {
        'Memoria Total (MB)': memoria_total,  # Convertimos a MB
        'Memoria Usada (MB)': memoria_usada,
        'Memoria Libre (MB)': memoria_libre,
    }
