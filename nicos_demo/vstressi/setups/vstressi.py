description = 'Virtual STRESS-SPEC instrument'

group = 'basic'

includes = [
    'system', 'sampletable', 'monochromator', 'detector', 'primaryslit',
    'slits', 'reactor'
]

sysconfig = dict(
    datasinks = ['caresssink', 'yamlsink'],
)

devices = dict(
    m1_foc = device('nicos.devices.generic.VirtualMotor',
        description = 'M1_FOC',
        fmtstr = '%.2f',
        unit = 'steps',
        abslimits = (0, 4096),
        speed = 10,
    ),
    m3_foc = device('nicos.devices.generic.VirtualMotor',
        description = 'M3_FOC',
        fmtstr = '%.2f',
        unit = 'steps',
        abslimits = (0, 4096),
        speed = 10,
    ),
    # histogram = device('nicos_mlz.frm2.devices.qmesydaqsinks.HistogramFileFormat',
    #     description = 'Histogram data written via QMesyDAQ',
    #     image = 'image',
    # ),
    # listmode = device('nicos_mlz.frm2.devices.qmesydaqsinks.ListmodeFileFormat',
    #     description = 'Listmode data written via QMesyDAQ',
    #     image = 'image',
    # ),
)

startupcode = '''
SetDetectors(adet)
'''
