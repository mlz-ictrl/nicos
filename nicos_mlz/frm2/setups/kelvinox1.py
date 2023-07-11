description = 'Kelvinox low temperature insert'

group = 'plugplay'

includes = ['alias_T']

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'T_{setupname}_sorb': device('nicos.devices.entangle.Sensor',
        description = 'Sorb temperature',
        tangodevice = tango_base + 'igh/sorb',
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 1,
        maxage = 2,
    ),
    f'T_{setupname}_pot':  device('nicos.devices.entangle.Sensor',
        description = '1K pot temperature',
        tangodevice = tango_base + 'igh/pot',
        unit = 'K',
        fmtstr = '%.3f',
        pollinterval = 1,
        maxage = 2,
    ),
    f'T_{setupname}_mix':  device('nicos.devices.entangle.Sensor',
        description = 'Mix chamber temperature',
        tangodevice = tango_base + 'igh/mix',
        unit = 'K',
        fmtstr = '%.4f',
        pollinterval = 1,
        maxage = 2,
    ),
}

alias_config = {
    'Ts':  {f'T_{setupname}_mix': 200},
}
