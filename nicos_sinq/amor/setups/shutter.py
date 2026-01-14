description = 'shutter control'

display_order = 33

devices = dict(
    shutter = device('nicos_sinq.devices.epics.shutter.Shutter',
                     description = 'Used to control the shutter',
                     shutterpvprefix = 'SQ:AMOR:SPS-SHUTTER',
                     ),
    )

