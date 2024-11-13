import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi.rfc1902 import *

async def snmp_walk(target, oid, community='public', port=161):
    results = []
    
    # Configuración del objetivo de transporte UDP
    transportTarget = await UdpTransportTarget.create((target, port))
    
    # Llamada a nextCmd para recorrer los OIDs
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
    

async def main():
    storage_results = await snmp_walk('192.168.1.3', '1.3.6.1.2.1.25.2.3.1')
    
    memoria_total = 0
    memoria_usada = 0
    hrStorageAllocationUnits = 0
    memoria_libre = 0
    index = 0
    
    for oid, value in storage_results:
        print(f'{oid.prettyPrint()} = {value.prettyPrint()}')
        if(oid.prettyPrint().startswith('SNMPv2-SMI::mib-2.25.2.3.1.1.')):
            index += 1
            continue
        elif(oid.prettyPrint() == 'SNMPv2-SMI::mib-2.25.2.3.1.5.'+str(index)):
            memoria_total = int(value.prettyPrint())
        elif(oid.prettyPrint() == 'SNMPv2-SMI::mib-2.25.2.3.1.6.'+str(index)):
            memoria_usada = int(value.prettyPrint())
        elif(oid.prettyPrint() == 'SNMPv2-SMI::mib-2.25.2.3.1.4.'+str(index)):
            hrStorageAllocationUnits = int(value.prettyPrint())
        else:
            continue        
        
    memoria_total = calc_memory(memoria_total, hrStorageAllocationUnits)
    memoria_usada = calc_memory(memoria_usada, hrStorageAllocationUnits)
    memoria_libre = memoria_total - memoria_usada

    print(f'Memoria Total: {memoria_total} MB')
    print(f'Memoria Usada: {memoria_usada} MB')
    print(f'Memoria Libre: {memoria_libre} MB')
    
def calc_memory(value, hrStorageAllocationUnits):
    return value * hrStorageAllocationUnits / (1024**3)
        
        
# Ejecutar el método main
if __name__ == "__main__":
    asyncio.run(main())
