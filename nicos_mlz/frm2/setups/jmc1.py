description = 'Juelich Motion Control Box Setup'

group = 'plugplay'

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    '%s_motor01' % setupname: device('nicos.devices.tango.Motor',
        description = 'JMC Motor 1',
        tangodevice = tango_base + 'motion/motor01',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
    '%s_motor02' % setupname: device('nicos.devices.tango.Motor',
        description = 'JMC Motor 2',
        tangodevice = tango_base + 'motion/motor02',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
    '%s_motor03' % setupname: device('nicos.devices.tango.Motor',
        description = 'JMC Motor 3',
        tangodevice = tango_base + 'motion/motor03',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
    '%s_motor04' % setupname: device('nicos.devices.tango.Motor',
        description = 'JMC Motor 4',
        tangodevice = tango_base + 'motion/motor04',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
}
