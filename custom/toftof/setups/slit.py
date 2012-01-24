description = 'sample slit'
includes = ['system']

nethost= '//toftofsrv.toftof.frm2/'

devices = dict(
    SampleSlitMotVB = device('nicos.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/ssbm',
                             fmtstr = "%7.3f"),
    SampleSlitMotVT = device('nicos.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/sstm',
                             fmtstr = "%7.3f"),
    SampleSlitMotHL = device('nicos.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/sslm',
                             fmtstr = "%7.3f"),
    SampleSlitMotHR = device('nicos.taco.motor.Motor',
                             tacodevice = nethost + 'toftof/huber/ssrm',
                             fmtstr = "%7.3f"),
    slit = device('nicos.generic.Slit',
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
