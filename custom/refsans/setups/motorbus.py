
description = 'IPC Motor bus device configuration'

includes = []

nethost = '//refsanssrv.refsans.frm2/'

devices = dict(
	motorbus = device('nicos.ipc.IPCModBusTaco', 
			tacodevice = nethost + 'test/ipcsms/1', 
                        loglevel = 'info',
                        timeout = 0.5,
			),

	motorbus2 = device('nicos.ipc.IPCModBusTaco', 
                        tacodevice = nethost + 'test/ipcsms/2',
                        loglevel = 'info',
                        timeout = 0.5,
			),
        )
