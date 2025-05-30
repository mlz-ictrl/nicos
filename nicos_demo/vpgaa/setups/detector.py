description = 'PGAA detectors'

group = 'lowlevel'

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
    image_60p = device('nicos_demo.vpgaa.devices.Spectrum',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        size = (16384, 1),
        visibility = (),
    ),
    _60p = device('nicos_demo.vpgaa.devices.DSPec',
        description = 'DSpec detector for high energy gamma x-rays ',
        timers = ['truetim', 'livetim'],
        images = ['image_60p'],
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
        pollinterval = None,
        liveinterval = 0.5,
        prefix = 'P'
    ),
    image_lege = device('nicos_demo.vpgaa.devices.Spectrum',
        description = 'Image data device',
        fmtstr = '%d',
        pollinterval = 86400,
        size = (16384, 1),
        visibility = (),
    ),
    LEGe = device('nicos_demo.vpgaa.devices.DSPec',
        description = 'DSpec detector for low energy gamma x-rays',
        timers = ['truetim', 'livetim'],
        images = ['image_lege'],
        gates = ['shutter'],
        enablevalues = ['open'],
        disablevalues = ['closed'],
        pollinterval = None,
        liveinterval = 0.5,
        prefix = 'L'
    ),
)
