description = 'LakeShore 331 temperature control/sensor'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    T_ls331_A = device('nicos.devices.tango.Sensor',
                     description = 'Sensor A of LakeShore',
                     tangodevice = tango_base + 'ls331/sensora',
                     unit = 'degC',
                     fmtstr = '%.2f',
                    ),
)

alias_config = {
    'Ts': {'T_ls331_A': 80}
}
