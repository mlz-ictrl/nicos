name = 'SINQ CrystalSample test devices'
description = 'Devices for testing CrystalSample code'

devices = dict(
    Sample = device('nicos_sinq.devices.sample.CrystalSample',
        description = 'SXTAL sample',
    ),
)
