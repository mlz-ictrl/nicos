description = 'Setup for a tensile machine from MLZ'

excludes = ['tensile']

# tango_host = 'dhcp02.ictrl.frm2.tum.de'
# tango_host = 'localhost.betrieb.frm2'
#tango_host = '172.25.189.224'
tango_host = '172.28.77.69'

tango_base = 'tango://%s:10000/test/doli/' % tango_host

devices = dict(
    teload = device('nicos.devices.entangle.Actuator',
        description = 'load value of the tensile machine',
        tangodevice = tango_base + 'force',
        fmtstr = '%.1f',
    ),
    tepos = device('nicos.devices.entangle.Actuator',
        description = 'position value of the tensile machine',
        tangodevice = tango_base + 'position',
        fmtstr = '%.4f',
    ),
    teext = device('nicos.devices.entangle.Actuator',
        description = 'extension value of the tensile machine',
        tangodevice = tango_base + 'extension',
        fmtstr = '%.6f',
    ),
)

display_order = 40
