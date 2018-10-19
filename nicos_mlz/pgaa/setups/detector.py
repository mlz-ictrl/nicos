description = 'PGAA detectors'

group = 'lowlevel'

tango_host = 'tango://silver.pgaa.frm2:10000/PGAA/MCA/'

devices = dict(
    _60p = device('nicos_mlz.pgaa.devices.DSPec',
        description = '60%',
        tangodevice = tango_host + '60',
        prefix = 'P',
        maxage = None,
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
    ),
    LEGe = device('nicos_mlz.pgaa.devices.DSPec',
        description = 'low energy germanium detector',
        tangodevice = tango_host + 'LEGe',
        prefix = 'L',
        maxage = None,
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
    ),
)
