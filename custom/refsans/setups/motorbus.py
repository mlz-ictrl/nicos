
description = 'IPC Motor bus device configuration'

includes = ['system']

nethost = "//refsanssrv.refsans.frm2/"

devices = dict(
	motorbus = device('nicos.ipc.IPCModBusTaco', 
			tacodevice = nethost + 'test/modbus/1', 
                        loglevel = 'info',
                        timeout = 0.5,
			),

	motorbus2 = device('nicos.ipc.IPCModBusTaco', 
			#tacodevice = nethost + 'test/ipcsms/1',
                        tacodevice = nethost + 'test/modbus/2',
                        loglevel = 'info',
                        timeout = 0.5,
			),
)
