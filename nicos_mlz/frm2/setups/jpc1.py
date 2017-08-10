description = 'JCNS pressure cell'
group = 'plugplay'

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'P_%s' % setupname: device('nicos.devices.tango.TemperatureController',
                               description = 'Pressure controller',
                               tangodevice = tango_base + 'eurotherm/control',
                               fmtstr = '%.1f',
                               unit = 'bar',
                              ),
}
