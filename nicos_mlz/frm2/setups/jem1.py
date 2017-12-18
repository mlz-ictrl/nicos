description = 'JCNS 2.2T electromagnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'I_%s' % setupname: device('nicos.devices.tango.PowerSupply',
        description = 'Magnet current',
        tangodevice = tango_base + 'bruker/supply',
        fmtstr = '%.1f',
        unit = 'A',
        timeout = 60.0,
        precision = 0.1,
    ),
    'B_%s' % setupname: device('nicos.devices.generic.CalibratedMagnet',
        currentsource = 'I_%s' % setupname,
        description = 'Magnet field',
        # abslimits are automatically determined from I
        unit = 'T',
        fmtstr = '%.4f',
        # calibration from measurement of A. Feoktystov
        # during cycle 39, fitted 2016-09-19
        calibration = (
            1.2833,
            65.032,
            0.035235,
            -127.25,
            0.029687
        )
    ),
    '%s_sam_trans' % setupname: device('nicos.devices.tango.Motor',
        description = 'Sample changer stage',
        tangodevice = tango_base + 'plc/plc_motor',
        fmtstr = '%.1f',
        unit = 'mm',
        precision = 0.1,
    ),
}

alias_config = {
    'B': {'B_%s' % setupname: 100, 'I_%s' % setupname: 80},
}
