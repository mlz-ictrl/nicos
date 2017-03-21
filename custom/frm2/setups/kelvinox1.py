description = 'Kelvinox low temperature insert'

group = 'plugplay'

includes = ['alias_T']

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'T_%s_sorb' % setupname: device('devices.tango.Sensor',
                                    description = 'Sorb temperature',
                                    tangodevice = tango_base + 'igh/sorb',
                                    unit = 'K',
                                    fmtstr = '%.3f',
                                    pollinterval = 1,
                                    maxage = 2,
                                   ),
    'T_%s_pot' % setupname:  device('devices.tango.Sensor',
                                    description = '1K pot temperature',
                                    tangodevice = tango_base + 'igh/pot',
                                    unit = 'K',
                                    fmtstr = '%.3f',
                                    pollinterval = 1,
                                    maxage = 2,
                                   ),
    'T_%s_mix' % setupname:  device('devices.tango.Sensor',
                                    description = 'Mix chamber temperature',
                                    tangodevice = tango_base + 'igh/mix',
                                    unit = 'K',
                                    fmtstr = '%.4f',
                                    pollinterval = 1,
                                    maxage = 2,
                                   ),

}

alias_config = {
    'Ts':  {'T_%s_mix' % setupname: 200},
}
