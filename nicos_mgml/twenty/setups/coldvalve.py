description = 'Control of VTI coldvalve'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/20t/'

devices = dict(
    cv_pressure = device('nicos.devices.entangle.TemperatureController',
        tangodevice = tango_base + 'coldvalve/pressurecontrol',
        loglevel = 'info',
        description = 'Coldvalve pressure regulation',
        fmtstr = '%.2f',
        unit = 'mBar'
    ),
    cv_output = device('nicos.devices.entangle.AnalogOutput',
        tangodevice = tango_base + 'coldvalve/output',
        loglevel = 'info',
        description = 'Coldvalve Manual output control',
        fmtstr = '%.2f',
        unit = '%'
    ),
    cv_mode = device('nicos.devices.entangle.NamedDigitalOutput',
        tangodevice = tango_base + 'coldvalve/mode',
        loglevel = 'info',
        description = 'Coldvalve Manual output control',
        mapping = {
            'automatic': 0,
            'manual': 1,
        },
        unit = '%'
    ),
)
