description = '3T High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'B_%s' % setupname: device('nicos.devices.entangle.RampActuator',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/magneticfield_cal',
        unit = 'T',
        fmtstr = "%.4f",
        abslimits = (-3, 3),
        precision = 0.0005,
    ),
    'B_%s_readback' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/currentmonitor_cal',
        unit = 'T',
        fmtstr = "%.4f",
        pollinterval = 1,
    ),
    '%s_T1' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the first stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t1',
        unit = 'K',
        warnlimits = (0, 44),
    ),
    '%s_T2' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the second stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t2',
        unit = 'K',
        warnlimits = (0, 12),
    ),
    '%s_TA' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack A',
        tangodevice = tango_base + 'hts_mss/t3',
        unit = 'K',
        warnlimits = (0, 18),
    ),
    '%s_TB' % setupname: device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack B',
        tangodevice = tango_base + 'hts_mss/t4',
        unit = 'K',
        warnlimits = (0, 18),
    ),
}

alias_config = {
    'B': {'B_%s' % setupname: 100},
}

extended = dict(
    representative = 'B_%s' % setupname,
)
