description = 'FRM II high temperature furnace'

group = 'optional'

includes = ['alias_T']

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    oven = device('nicos.devices.taco.TemperatureController',
        description = 'High temperature furnace controller',
        tacodevice = '//%s/toftof/htf/control' % nethost,
        userlimits = (0, 2000),
        abslimits = (0, 2000),
        ramp = 0.1,
        unit = 'C',
        fmtstr = '%.3f',
    ),
)

alias_config = {
    'T': {'oven': 0},
    'Ts': {'oven': 0},
}
