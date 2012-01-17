includes = ['system']

nethost= '//toftofsrv.toftof.frm2/'

devices = dict(
    SampleSlitMotVB = device('nicos.taco.motor.Motor',
		tacodevice = nethost + 'toftof/huber/ssbm',
		fmtstr = "%7.3f",
		abslimits = (-200.0, 46.425),
		),
    SampleSlitMotVT = device('nicos.taco.motor.Motor',
		tacodevice = nethost + 'toftof/huber/sstm',
		fmtstr = "%7.3f",
		abslimits = (-200.0, 46.425),
		),
    SampleSlitMotHL = device('nicos.taco.motor.Motor',
		tacodevice = nethost + 'toftof/huber/sslm',
		fmtstr = "%7.3f",
		abslimits = (-200.0, 27.5),
		),
    SampleSlitMotHR = device('nicos.taco.motor.Motor',
		tacodevice = nethost + 'toftof/huber/ssrm',
		fmtstr = "%7.3f",
		abslimits = (-200.0, 27.5),
		),
    SampleSlit = device('nicos.generic.Slit',
		bottom = 'SampleSlitMotVB',
		top = 'SampleSlitMotVT',
		left = 'SampleSlitMotHL',
		right = 'SampleSlitMotHR',
		opmode = 'offcentered',
		),

)

startupcode = """
ssvg = SampleSlit.height
ssvo = SampleSlit.centery
sshg = SampleSlit.width
ssho = SampleSlit.centerx
"""
