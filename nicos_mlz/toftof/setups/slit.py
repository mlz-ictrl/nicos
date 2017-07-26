description = 'sample slit'

group = 'lowlevel'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    SampleSlitMotVB = device('nicos.devices.taco.motor.Motor',
                             lowlevel = True,
                             tacodevice = '//%s/toftof/huber/ssbm' % (nethost,),
                             fmtstr = "%7.3f",
                            ),
    SampleSlitMotVT = device('nicos.devices.taco.motor.Motor',
                             lowlevel = True,
                             tacodevice = '//%s/toftof/huber/sstm' % (nethost,),
                             fmtstr = "%7.3f",
                            ),
    SampleSlitMotHL = device('nicos.devices.taco.motor.Motor',
                             lowlevel = True,
                             tacodevice = '//%s/toftof/huber/sslm' % (nethost,),
                             fmtstr = "%7.3f",
                            ),
    SampleSlitMotHR = device('nicos.devices.taco.motor.Motor',
                             lowlevel = True,
                             tacodevice = '//%s/toftof/huber/ssrm' % (nethost,),
                             fmtstr = "%7.3f",
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
