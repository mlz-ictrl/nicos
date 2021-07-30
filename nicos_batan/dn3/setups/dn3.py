description = 'Simulated DN3 instrument'

group = 'basic'

sysconfig = dict(
    datasinks = ['dn3sink'],
)

includes = ['detector', 'monochromator']  # 'source']

devices = dict(
    tths = device('nicos.devices.generic.Axis',
        description = 'Simulated 2ThetaSample',
        fmtstr = '%.2f',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-170, 8),
        ),
        precision = 0.05,
    ),
    ths = device('nicos.devices.generic.VirtualMotor',
        description = 'Simulated ThetaSample',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (-360, 360),
    ),
    tthm = device('nicos.devices.generic.ManualSwitch',
        description = '2Theta Monochromator',
        states = ['45', '90', '135'],
        unit = 'deg',
    ),
    dn3sink = device('nicos_batan.dn3.devices.datasinks.DN3Sink',
        description = 'DN3 specific data file format',
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.txt'],
        detectors = ['adet'],
    ),
)
# display_order = 40
