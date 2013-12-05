description = 'hv testing'
group = 'optional'

includes = ['system']

devices = dict(
    hv_supply   = device('devices.generic.VirtualMotor',
                      abslimits = (0, 1550),
                      unit = 'V',
                     ),
    hv_sw    = device('devices.generic.ManualMove',
                      abslimits = (0, 1),
                      unit = '',
                     ),
    hv    = device('sans1.hv.Sans1HV',
                      unit = 'V',
                      supply = 'hv_supply',
                      discharger = 'hv_sw',
                     ),
)
