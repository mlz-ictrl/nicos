description = 'Sample surface position measurement'

group = 'optional'

tango_base = 'tango://refsanshw.refsans.frm2:10000/refsans/'

devices = dict(
    height = device('nicos.devices.tango.Sensor',
        description = 'Sample surface position, offset in entangle. Access via '
                      'quango.',
        tangodevice = tango_base + 'keyence/sensor',
        unit = 'mm',
    ),
)
