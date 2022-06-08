description = 'memograph readout'

group = 'optional'
tango_host = 'tango://ictrlfs.ictrl.frm2:10000/'

devices = {}

instrs = sorted(['biodiff', 'dns', 'panda', 'jnse', 'kws1', 'kws2', 'kws3',
                 'poli', 'maria', 'treff', 'spheres'])
memographs = {
    'biodiff': 'memograph09/BioDiff/',
    'dns': 'memograph02/DNS/',
    'panda': 'memograph-uja04/PANDA/',
    'jnse': 'memograph09/NSE/',
    'kws1': 'memograph03/KWS/',
    'kws2': 'memograph03/KWS/',
    'kws3': 'memograph09/KWS123/',
    'poli': 'memograph-uja01/POLI/',
    'maria': 'memograph04/MARIA/',
    'treff': 'memograph04/TREFF/',
    'spheres': 'memograph03/SPHERES/',
}

for instr in instrs:
    tango_base = tango_host + memographs[instr]
    devices[instr + '_cooling_t_in'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet temperature',
        tangodevice = tango_base + 'T_in',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_t_out'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet temperature',
        tangodevice = tango_base + 'T_out',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_p_in'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet pressure',
        tangodevice = tango_base + 'P_in',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_p_out'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet pressure',
        tangodevice = tango_base + 'P_out',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_flow_in'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet flow',
        tangodevice = tango_base + 'FLOW_in',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_flow_out'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet flow',
        tangodevice = tango_base + 'FLOW_out',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_leak'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling leak flow',
        tangodevice = tango_base + 'Leak',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )
    devices[instr + '_cooling_power'] = device('nicos.devices.entangle.Sensor',
        description = 'Cooling power',
        tangodevice = tango_base + 'Cooling',
        pollinterval = 30,
        maxage = 60,
        fmtstr = '%.2f',
    )

del devices['jnse_cooling_flow_out']
del devices['jnse_cooling_leak']
