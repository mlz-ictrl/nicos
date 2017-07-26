description = 'Simulated HRPD instrument'

group = 'basic'

excludes = []

sysconfig = dict(
    datasinks = ['hrpdsink'],
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
    hrpdsink = device('nicos_mlz.hrpd.devices.datasinks.HrpdSink',
        description = 'HRPD specific data file format',
        lowlevel = True,
        filenametemplate = ['%(proposal)s_%(pointcounter)08d.txt'],
        detectors = ['adet'],
    ),
)
# display_order = 40
