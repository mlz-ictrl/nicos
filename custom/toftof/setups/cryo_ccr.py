description = 'FRM II CCR box with LakeShore LS336 controller'

group = 'optional'

includes = ['alias_T']

nethost = 'ccr17'

devices = dict(
    cryo   = device('devices.taco.TemperatureController',
                    description = 'The control device to the sample',
                    tacodevice = '//%s/ccr/ls336/control2' % nethost,
                    userlimits = (0, 600),
                    abslimits = (0, 600),
                    p = 50,
                    i = 10,
                    d = 0,
                    ramp = 6.0,
                    unit = 'K',
                    fmtstr = '%g',
                   ),

    cryo_tube = device('devices.taco.TemperatureController',
                       description = 'The control device of the tube',
                       tacodevice = '//%s/ccr/ls336/control1' % nethost,
                       userlimits = (0, 400),
                       abslimits = (0, 400),
                       p = 50,
                       i = 10,
                       d = 0,
                       ramp = 6.0,
                       unit = 'K',
                       fmtstr = '%g',
                      ),

    cryo_a = device('devices.taco.TemperatureSensor',
                    description = 'Temperature at the tube',
                    tacodevice = '//%s/ccr/ls336/sensora' % nethost,
                    unit = 'K',
                    fmtstr = '%g',
                   ),

    cryo_b = device('devices.taco.TemperatureSensor',
                    description = 'Temperature at the tube',
                    tacodevice = '//%s/ccr/ls336/sensorb' % nethost,
                    unit = 'K',
                    fmtstr = '%g',
                   ),

    cryo_c = device('devices.taco.TemperatureSensor',
                    description = 'Temperature at the sample stick',
                    tacodevice = '//%s/ccr/ls336/sensorc' % nethost,
                    unit = 'K',
                    fmtstr = '%g',
                   ),

    cryo_d = device('devices.taco.TemperatureSensor',
                    description = 'Temperature at the sample stick',
                    tacodevice = '//%s/ccr/ls336/sensord' % nethost,
                    unit = 'K',
                    fmtstr = '%g',
                   ),

    cryo_machine = device('devices.taco.DigitalOutput',
                          description = 'Switch for the compressor',
                          tacodevice = '//%s/ccr/plc/on' % nethost,
                         ),

    cryo_gs = device('devices.taco.DigitalOutput',
                     lowlevel = True,
                     tacodevice = '//%s/ccr/plc/gas' % nethost,
                    ),

    cryo_gr = device('devices.taco.DigitalInput',
                     lowlevel = True,
                     tacodevice = '//%s/ccr/plc/fbgas' % nethost,
                    ),

    cryo_g = device('devices.vendor.frm2.CCRSwitch',
                    description = 'Gas valve switch',
                    write = 'cryo_gs',
                    feedback = 'cryo_gr',
                   ),

    cryo_vs = device('devices.taco.DigitalOutput',
                     lowlevel = True,
                     tacodevice = '//%s/ccr/plc/vacuum' % nethost,
                    ),

    cryo_vr= device('devices.taco.DigitalInput',
                    lowlevel = True,
                    tacodevice = '//%s/ccr/plc/fbvacuum' % nethost,
                   ),

    cryo_v = device('devices.vendor.frm2.CCRSwitch',
                    description = 'Vacuum valve switch',
                    write = 'cryo_vs',
                    feedback = 'cryo_vr',
                   ),

    cryo_p = device('devices.taco.AnalogInput',
                    description = 'Pressure in the vacuum chamber',
                    tacodevice = '//%s/ccr/plc/p2' % nethost,
                    fmtstr = '%.4g',
                    unit = 'mbar',
                   ),
)

alias_config = {
    'T':  {'cryo': 100},
    'Ts': {'cryo_c': 100, 'cryo_d': 90, 'cryo_a': 80, 'cryo_b': 70},
}
