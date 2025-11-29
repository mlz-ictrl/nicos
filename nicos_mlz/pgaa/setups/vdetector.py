description = 'PGAA detectors'

group = 'lowlevel'

excludes = ['detector']

devices = dict(
    truetim = device('nicos.devices.generic.VirtualTimer',
        description = 'True time timer',
        fmtstr = '%.2f',
        unit = 's',
        visibility = (),
    ),
    livetim = device('nicos.devices.generic.VirtualTimer',
        description = 'Live time timer',
        fmtstr = '%.2f',
        unit = 's',
        visibility = (),
    ),
    image = device('nicos_virt_mlz.pgaa.devices.DSPecSpectrum',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        size = (16384, 1),
        visibility = (),
        prefix = '',
    ),
    _60p = device('nicos_virt_mlz.pgaa.devices.DSPec',
        description = 'DSpec detector for high energy gamma x-rays ',
        timers = ['truetim', 'livetim'],
        images = ['image'],
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
        pollinterval = None,
        liveinterval = 0.5,
        prefix = 'P'
    ),
    LEGe = device('nicos_virt_mlz.pgaa.devices.DSPec',
        description = 'DSpec detector for low energy gamma x-rays',
        timers = ['truetim', 'livetim'],
        images = ['image'],
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
        pollinterval = None,
        liveinterval = 0.5,
        prefix = 'L'
    ),
)
