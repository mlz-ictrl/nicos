description = 'memograph readout (cooling system)'

group = 'lowlevel'

tango_base = 'tango://ictrlfs.ictrl.frm2.tum.de:10000/memograph07/REFSANS/'

lowlevel = ('namespace', 'devlist', 'metadata')

devices = dict(
    t_memograph_in = device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet temperature',
        tangodevice = tango_base + 'T_in',
        fmtstr = '%.2f',
        warnlimits = (-1, 17.5),  # -1 no lower value
        unit = 'degC',
        visibility = lowlevel,
    ),
    t_memograph_out = device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet temperature',
        tangodevice = tango_base + 'T_out',
        fmtstr = '%.2f',
        unit = 'degC',
        visibility = lowlevel,
    ),
    p_memograph_in = device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet pressure',
        tangodevice = tango_base + 'P_in',
        fmtstr = '%.2f',
        unit = 'bar',
        visibility = lowlevel,
    ),
    p_memograph_out = device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet pressure',
        tangodevice = tango_base + 'P_out',
        fmtstr = '%.2f',
        unit = 'bar',
        visibility = lowlevel,
    ),
    flow_memograph_in = device('nicos.devices.entangle.Sensor',
        description = 'Cooling inlet flow',
        tangodevice = tango_base + 'FLOW_in',
        fmtstr = '%.2f',
        warnlimits = (0.2, 100),  # 100 no upper value
        unit = 'l/min',
        visibility = lowlevel,
    ),
    flow_memograph_out = device('nicos.devices.entangle.Sensor',
        description = 'Cooling outlet flow',
        tangodevice = tango_base + 'FLOW_out',
        fmtstr = '%.2f',
        unit = 'l/min',
        visibility = lowlevel,
    ),
    leak_memograph = device('nicos.devices.entangle.Sensor',
        description = 'Cooling leakage',
        tangodevice = tango_base + 'Leak',
        fmtstr = '%.2f',
        warnlimits = (-1, 1),  # -1 no lower value
        unit = 'l/min',
        visibility = lowlevel,
    ),
    cooling_memograph = device('nicos.devices.entangle.Sensor',
        description = 'Cooling power',
        tangodevice = tango_base + 'Cooling',
        fmtstr = '%.2f',
        unit = 'kW',
        visibility = lowlevel,
    ),
)
