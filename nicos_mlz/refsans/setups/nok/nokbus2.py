group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

description = 'IPC Motor bus device configuration'

includes = []

# data from instrument.inf
# used for:
# - nok4 reactor side (addr 0x36)
# - zb0 (addr 0x37)
# - zb1 (addr 0x38)
#

devices = dict(
    nokbus2 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        tacodevice = '//%s/test/network/ipcsms_2' % (nethost,),
        loglevel = 'info',
        lowlevel = True,
        bustimeout = 0.5,
    ),
)
