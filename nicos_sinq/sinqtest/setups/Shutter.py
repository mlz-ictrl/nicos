description = 'Shutter Control'

devices = dict(
    Shutter = device('nicos_sinq.devices.epics.shutter.Shutter',
        description = 'Used to control the shutter',
        shutterpvprefix = 'SQ:SINQTEST:SPS-SHUTTER',
    ),
)
