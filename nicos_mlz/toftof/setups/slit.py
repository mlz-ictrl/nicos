description = 'sample slit'

group = 'lowlevel'

tango_base = 'tango://tofhw.toftof.frm2.tum.de:10000/toftof/hubermc/'

devices = dict(
    SampleSlitMotVB = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'ssbm',
        fmtstr = '%7.3f',
    ),
    SampleSlitMotVT = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'sstm',
        fmtstr = '%7.3f',
    ),
    SampleSlitMotHL = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'sslm',
        fmtstr = '%7.3f',
    ),
    SampleSlitMotHR = device('nicos.devices.tango.Motor',
        lowlevel = True,
        tangodevice = tango_base + 'ssrm',
        fmtstr = '%7.3f',
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
