description = 'Impac IGAR 12-LO pyrometer'

group = 'optional'

includes = ['alias_T']

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/rs232/'

devices = dict(
    pyro = device('nicos_mlz.toftof.devices.impac.TemperatureSensor',
        description = 'Impac pyrometer thermometer',
        tangodevice = tango_base + 'ifpyrometer',
        unit = 'C',
        fmtstr = '%.3f',
    ),
)

alias_config = {
    'T':  {'pyro': 100},
    'Ts': {'pyro': 100},
}
