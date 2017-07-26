group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

description = 'IPC Motor bus device configuration'

includes = []

devices = dict(
    nokbus3 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                      tacodevice = '//%s/test/network/ipcsms_3' % (nethost,),
                      loglevel = 'info',
                      lowlevel = True,
                      bustimeout = 0.5,
            ),
)
