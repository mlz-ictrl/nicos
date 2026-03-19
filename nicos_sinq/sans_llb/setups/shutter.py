description = 'Devices for the shutter at SANS-LLB'

spsprefix = 'SQ:SANS-LLB:SPS-SHUTTER'
hide = True

group = 'lowlevel'

devices = dict(
    shutter = device('nicos_sinq.sans_llb.devices.shutter.Shutter',
          pvprefix = spsprefix,
          description = 'Control SANS-LLB instrument shutter and report access status',
    ),
)
