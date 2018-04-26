description = 'Analyzer alias device(s)'

group = 'lowlevel'

devices = dict(
    ana = device('nicos.devices.generic.DeviceAlias',
        description = 'analyser alias device',
        alias = 'ana_pg002',
        devclass = 'nicos.devices.tas.Monochromator',
    ),
)
