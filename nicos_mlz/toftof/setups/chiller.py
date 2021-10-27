description = 'Chopper cooling water chiller (TermoTek)'

group = 'lowlevel'

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/termotek/'

devices = dict(
    t_in_chopper = device('nicos.devices.entangle.Sensor',
        description = 'Temperature of the chopper cooling water inlet',
        tangodevice = tango_base + 'tout1',
        fmtstr = '%.2f',
    ),
    p_in_chopper = device('nicos.devices.entangle.Sensor',
        description = 'Pressure of the chopper cooling water inlet',
        tangodevice = tango_base + 'pressure',
        fmtstr = '%.2f',
    ),
    flow_in_chopper = device('nicos.devices.entangle.Sensor',
        description = 'Water flow of the chopper cooling water inlet',
        tangodevice = tango_base + 'flow1',
        fmtstr = '%.2f',
    ),
    water_level_chopper =  device('nicos.devices.generic.ReadonlySwitcher',
        description = 'Water level status in TermoTek chiller',
        readable = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + 'level',
        ),
        fmtstr = '%s',
        mapping = {
            'OK': 0,
            'WARNING': 1,
            'ALARM': 2,
        },
    ),
)
