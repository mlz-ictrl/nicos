description = 'IPC Motor bus device configuration'

includes = []

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    motorbus = device('devices.vendor.ipc.IPCModBusTaco',
                      tacodevice = '//%s/test/ipcsms/1' % (nethost,),
                      loglevel = 'info',
                      lowlevel = True,
                      bustimeout = 0.5,
            ),
    motorbus2 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = '//%s/test/ipcsms/2' % (nethost,),
                       loglevel = 'info',
                       lowlevel = True,
                       bustimeout = 0.5,
            ),
    motorbus3 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = '//%s/test/ipcsms/3' % (nethost,),
                       loglevel = 'info',
                       lowlevel = True,
                       bustimeout = 0.5,
            ),
    motorbus4 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = '//%s/test/ipcsms/4' % (nethost,),
                       lowlevel = True,
                       loglevel = 'info',
                       bustimeout = 0.5,
            ),
)
