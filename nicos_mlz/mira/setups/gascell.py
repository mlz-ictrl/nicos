description = 'alfonso pressure module'
group = 'optional'

tango_base = 'tango://e21-92.mira.frm2:10000/mira/'

devices = dict(
    diptron3plus = device('nicos.devices.entangle.AnalogInput',
        tangodevice = tango_base + 'alfonsomodule/diptron3',
        description = 'Pressure at Diptron 3 Plus',
        pollinterval = 0.7,
        maxage = 2,
        fmtstr = '%.3f',
        unit = 'bar',
    ),
    sentronicplus = device('nicos.devices.entangle.Actuator',
        tangodevice = tango_base + 'alfonsomodule/sentronic',
        description = 'Sentronic PLUS digital proportioning valve',
        warnlimits = (0, 10.0),
        pollinterval = 0.7,
        maxage = 2,
        fmtstr = '%.3f',
        unit = 'bar',
    ),
    kistler = device('nicos.devices.entangle.AnalogInput',
        tangodevice = tango_base + 'alfonsomodule/kistler',
        description = 'Kistler Charge Meter for Calibration with Piezo Sensor',
        pollinterval = 0.7,
        maxage = 2,
        fmtstr = '%.3f',
        unit = 'N',
    ),
)
