description = 'Refsans 4 analog 1 GPIO on Raspberry'

group = 'plugplay'

tango_base = 'tango://%s:10000/test/ads/' % setupname

devices = {
    '%s_ch1' % setupname : device('nicos.devices.tango.Sensor',
        description = 'ADin0',
        tangodevice = tango_base + 'ch1',
        unit = 'foo',
        fmtstr = '%.4f',
    ),
    '%s_ch2' % setupname : device('nicos.devices.tango.Sensor',
        description = 'ADin1',
        tangodevice = tango_base + 'ch2',
        unit = 'foo',
        fmtstr = '%.4f',
    ),
    '%s_ch3' % setupname : device('nicos.devices.tango.Sensor',
        description = 'ADin2',
        tangodevice = tango_base + 'ch3',
        unit = 'foo',
        fmtstr = '%.4f',
    ),
    '%s_ch4' % setupname : device('nicos.devices.tango.Sensor',
        description = 'ADin3',
        tangodevice = tango_base + 'ch4',
        unit = 'foo',
        fmtstr = '%.4f',
    ),
}
