description = 'pressure sensors connected to the chambers'

group = 'lowlevel'

includes = ['vsd']

devices = dict(
    chamber_CB = device('nicos_mlz.refsans.devices.converters.Ttr',
        description = 'pressure sensor connected to the CB',
        unit = 'mbar',
        att = 'X16Voltage1',
    ),
    chamber_SFK = device('nicos_mlz.refsans.devices.converters.Ttr',
        description = 'pressure sensor connected to the SFK',
        unit = 'mbar',
        att = 'X16Voltage2',
    ),
    chamber_SR = device('nicos_mlz.refsans.devices.converters.Ttr',
        description = 'pressure sensor connected to the SR',
        unit = 'mbar',
        att = 'X16Voltage3',
    ),
)
