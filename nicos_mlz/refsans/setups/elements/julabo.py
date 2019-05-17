description = 'REFSANS setup for julabo01 Presto A40'

group = 'optional'

tango_base = 'tango://refsanshw.refsans.frm2:10000/refsans/'

devices = dict(
    julabo_temp = device('nicos.devices.tango.TemperatureController',
        description = 'julabo01 temperature',
        tangodevice = tango_base + 'julabo01/control',
    ),
)
