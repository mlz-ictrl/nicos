description = 'sample slit'

group = 'lowlevel'

devices = dict(
    SampleSlitMotVB = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = (-200, 46.425),
        fmtstr = "%7.3f",
        unit = 'mm',
        speed = 3,
    ),
    SampleSlitMotVT = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = (-200, 46.425),
        fmtstr = "%7.3f",
        unit = 'mm',
        speed = 3,
    ),
    SampleSlitMotHL = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = (-200, 27.5),
        fmtstr = "%7.3f",
        unit = 'mm',
        speed = 3,
    ),
    SampleSlitMotHR = device('nicos.devices.generic.VirtualMotor',
        lowlevel = True,
        abslimits = (-200, 27.5),
        fmtstr = "%7.3f",
        unit = 'mm',
        speed = 3,
    ),
    slit = device('nicos.devices.generic.Slit',
        description = 'Sample entry slit',
        bottom = 'SampleSlitMotVB',
        top = 'SampleSlitMotVT',
        left = 'SampleSlitMotHL',
        right = 'SampleSlitMotHR',
        coordinates = 'opposite',
        opmode = 'offcentered',
    ),
)

startupcode = '''
ssvg = slit.height
ssvo = slit.centery
sshg = slit.width
ssho = slit.centerx
'''
