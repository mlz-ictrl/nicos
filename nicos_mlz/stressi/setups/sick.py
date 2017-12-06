description = 'Sick distance laser device'

group = 'optional'

tango_base = 'tango://stressictrl.stressi.frm2:10000/stressi/'

devices = dict(
    sick = device('nicos.devices.tango.Sensor',
        description = 'Laser distance detecting device',
        tangodevice = tango_base + 'sick/sensor',
        unit = 'mm',
    ),
)
