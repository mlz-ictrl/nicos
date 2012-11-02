description = 'sample slit'
includes = ['system']

nethost= '//toftofsrv.toftof.frm2/'

devices = dict(
    SampleSlitMotVB = device('devices.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/ssbm',
                             fmtstr = "%7.3f"),
    SampleSlitMotVT = device('devices.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/sstm',
                             fmtstr = "%7.3f"),
    SampleSlitMotHL = device('devices.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/sslm',
                             fmtstr = "%7.3f"),
    SampleSlitMotHR = device('devices.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/ssrm',
                             fmtstr = "%7.3f"),
    slit = device('devices.generic.Slit',
                  bottom = 'SampleSlitMotVB',
                  top = 'SampleSlitMotVT',
                  left = 'SampleSlitMotHL',
                  right = 'SampleSlitMotHR',
                  coordinates = 'opposite',
                  opmode = 'offcentered'),
)

startupcode = """
ssvg = slit.height
ssvo = slit.centery
sshg = slit.width
ssho = slit.centerx
"""
