import asyncio
from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi.rfc1902 import *

async def snmp_walk(target, oid, community='public', port=161):
    results = []
    
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

async def get_cpu_load(target, community='public', port=161):
    cpu_load_oid = '1.3.6.1.2.1.25.3.3.1.2'
    cpu_load_results = await snmp_walk(target, cpu_load_oid, community, port)
    
    total_load = 0
    count = 0
    for oid, value in cpu_load_results:
        print(f'{oid.prettyPrint()} = {value.prettyPrint()}%')
        total_load += int(value.prettyPrint())
        count += 1
    
    if count > 0:
        avg_cpu_load = total_load / count
        print(f'Total CPU Load: {total_load}%')
        print(f'Average CPU Load: {avg_cpu_load:.2f}%')
    else:
        print("No CPU load data found.")
        
    return avg_cpu_load if count > 0 else None

async def main():
    cpu_load = await get_cpu_load('192.168.1.3') 
    
if __name__ == "__main__":
    asyncio.run(main())