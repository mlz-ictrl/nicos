group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

description = 'IPC Motor bus device configuration'

includes = []

devices = dict(
    nokbus4 = device('devices.vendor.ipc.IPCModBusTaco',
                      tacodevice = '//%s/test/ipcsms/4' % (nethost,),
                      loglevel = 'info',
                      lowlevel = True,
                      bustimeout = 0.5,
            ),
)
