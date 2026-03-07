description = 'Devices for the shutter at SANS-LLB'

spsprefix = 'SQ:SANS-LLB:SPS-SHUTTER'
hide = True

group = 'lowlevel'

devices = dict(
    shutter = device('nicos_sinq.devices.epics.shutter.Shutter',
          shutterpvprefix = spsprefix,
          description = 'Control SANS-LLB instrument shutter and report access status',
    ),
)
