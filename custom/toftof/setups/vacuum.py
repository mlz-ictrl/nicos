includes = ['system']


devices = dict(
    vacbus = device('nicos.toftof.toni.ModBus',
		tacodevice = '//toftofsrv/toftof/rs232/ifvacuumcontrol',
                lowlevel = True,
		),
    vac0 = device('nicos.toftof.toni.Vacuum', 
                  bus = 'vacbus',
                  power = 0,
                  channel = 0,
		  addr = 240,
		  fmtstr = '%g'
                  ),
    vac1 = device('nicos.toftof.toni.Vacuum', 
                  bus = 'vacbus',
                  power = 0,
                  channel = 1,
		  addr = 240,
		  fmtstr = '%g'
                  ),
    vac2 = device('nicos.toftof.toni.Vacuum', 
                  bus = 'vacbus',
                  power = 0,
                  channel = 2,
		  addr = 240,
		  fmtstr = '%g'
                  ),
    vac3 = device('nicos.toftof.toni.Vacuum', 
                  bus = 'vacbus',
                  power = 0,
                  channel = 3,
		  addr = 240,
		  fmtstr = '%g'
                  ),
)
