description = 'JCNS gas pressure cell T1001'
group = 'plugplay'

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'P_%s' % setupname: device('nicos.devices.tango.Sensor',
                               description = 'Pressure readout',
                               tangodevice = tango_base + 'beckhoff/pressure',
                               fmtstr = '%.3f',
                               unit = 'bar',
                              ),
    'P_%s_pump' % setupname: device('nicos.devices.tango.WindowTimeoutAO',
                                    description = 'Pressure at the pump',
                                    tangodevice = tango_base + 'pump/pressure',
                                    fmtstr = '%.1f',
                                    precision = 0.1,
                                    window = 30,
                                    timeout = 1800,
                                   ),
}
