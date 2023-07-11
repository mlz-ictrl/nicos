description = '3T High-Tc superconducting magnet'

group = 'plugplay'

includes = ['alias_B']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'B_{setupname}': device('nicos.devices.entangle.RampActuator',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/magneticfield_cal',
        unit = 'T',
        fmtstr = "%.4f",
        abslimits = (-3, 3),
        precision = 0.0005,
    ),
    f'B_{setupname}_readback': device('nicos.devices.entangle.AnalogInput',
        description = 'magnetic field device',
        tangodevice = tango_base + 'plc/currentmonitor_cal',
        unit = 'T',
        fmtstr = "%.4f",
        pollinterval = 1,
    ),
    f'{setupname}_T1': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the first stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t1',
        unit = 'K',
        warnlimits = (0, 44),
    ),
    f'{setupname}_T2': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of the second stage of the '
        'cryo-cooler',
        tangodevice = tango_base + 'hts_mss/t2',
        unit = 'K',
        warnlimits = (0, 12),
    ),
    f'{setupname}_TA': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack A',
        tangodevice = tango_base + 'hts_mss/t3',
        unit = 'K',
        warnlimits = (0, 18),
    ),
    f'{setupname}_TB': device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature of coil pack B',
        tangodevice = tango_base + 'hts_mss/t4',
        unit = 'K',
        warnlimits = (0, 18),
    ),
}

alias_config = {
    'B': {f'B_{setupname}': 100},
}

extended = dict(
    representative = f'B_{setupname}',
)
