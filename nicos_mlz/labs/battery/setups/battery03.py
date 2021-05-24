description = 'Battery temperature sensors'

# Devices run on a raspberry as entangle devices

tangobase = 'tango://%s:10000/box/sensor/' % setupname

group = 'plugplay'

devices = dict(
)

for i in range(1, 9):
    devices['T_%s_%d' % (setupname, i)] = device('nicos.devices.tango.Sensor',
        description = '%s temperature %d' % (setupname.capitalize(), i),
        tangodevice = tangobase + '%d' % i,
        pollinterval = 30,
        maxage = 35,
    )
