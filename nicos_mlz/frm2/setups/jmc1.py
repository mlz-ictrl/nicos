description = 'Juelich Motion Control Box Setup'

group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'{setupname}_motor01': device('nicos.devices.entangle.Motor',
        description = 'JMC Motor 1',
        tangodevice = tango_base + 'motion/motor01',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
    f'{setupname}_motor02': device('nicos.devices.entangle.Motor',
        description = 'JMC Motor 2',
        tangodevice = tango_base + 'motion/motor02',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
    f'{setupname}_motor03': device('nicos.devices.entangle.Motor',
        description = 'JMC Motor 3',
        tangodevice = tango_base + 'motion/motor03',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
    f'{setupname}_motor04': device('nicos.devices.entangle.Motor',
        description = 'JMC Motor 4',
        tangodevice = tango_base + 'motion/motor04',
        fmtstr = '%.1f',
        unit = '',
        precision = 0.1,
    ),
}
