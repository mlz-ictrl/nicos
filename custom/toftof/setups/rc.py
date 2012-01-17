includes = ['system']


devices = dict(
    rcbus = device('nicos.toftof.rc.ModBusDriverHP',
		tacodevice = '//toftofsrv/toftof/rs232/ifhubermot1',
                maxtries = 5,
                lowlevel = False,
		),
    rc = device('nicos.toftof.rc.RadialCollimator', 
                 bus = 'rcbus',
		 address = 13,
        	 start_angle = 1.0,
                 stop_angle = 5.4,
                 std_speed = 120,
                 ref_speed = 100,
                 timeout = 120,
                 unit = 'deg',
		 fmtstr = '%g'
                ),
)
