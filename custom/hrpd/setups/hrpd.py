description = 'Simulated HRPD instrument'

group = 'basic'

excludes = []

sysconfig = dict(
    datasinks = ['hrpdsink'],
)

includes = ['detector', 'monochromator']  # 'source']

devices = dict(
    tths = device('devices.generic.Axis',
        description = 'Simulated 2ThetaSample',
        fmtstr = '%.2f',
        motor = device('devices.generic.VirtualMotor',
            unit = 'deg',
            abslimits = (-170, 8),
        ),
        precision = 0.05,
    ),
    ths = device('devices.generic.VirtualMotor',
        description = 'Simulated ThetaSample',
        fmtstr = '%.2f',
        unit = 'deg',
        abslimits = (-360, 360),
    ),
    tthm = device('devices.generic.ManualSwitch',
        description = '2Theta Monochromator',
        states = ['45', '90', '135'],
    ),
    hrpdsink = device('spodi.datasinks.CaressHistogram',
        description = 'SPODI specific histogram file format',
        lowlevel = True,
        filenametemplate = ['m1%(pointcounter)08d.ctxt'],
        detectors = ['adet'],
    ),
)
# display_order = 40
