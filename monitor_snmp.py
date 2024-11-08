import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def obtener_datos_snmp(host='localhost', comunidad='public', oid='1.3.6.1.2.1.25.2.2.0'):
    resultado = {}
    snmpEngine = SnmpEngine()

    iterator = get_cmd(
        snmpEngine,
        CommunityData(comunidad, mpModel=0),
        await UdpTransportTarget.create((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(errorIndication)
        return None

    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
        return None
    else:
        for varBind in varBinds:
            resultado[str(varBind[0])] = int(varBind[1])

    snmpEngine.close_dispatcher()
    return resultado