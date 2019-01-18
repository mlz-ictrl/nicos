description = 'Sample surface position measurement'

group = 'optional'

tango_base = 'tango://refsanshw.refsans.frm2:10000/refsans/'

devices = dict(
    height = device('nicos_mlz.refsans.devices.tristate.TriState',
        description = 'Sample surface position.',
        unit = 'mm',
        port = 'height_port',
    ),
    height_port = device('nicos.devices.tango.Sensor',
        description = 'Sample surface position',
        tangodevice = tango_base + 'keyence/sensor',
        unit = 'mm',
        lowlevel = True,
    ),
)
