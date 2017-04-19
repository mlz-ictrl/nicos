group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

description = 'IPC Motor bus device configuration'

includes = []

# data from instrument.inf
# used for:
# - nok1 (addr 0x31)
# - nok2 (addr 0x32, 0x33)
# - nok3 (addr 0x34, 0x35)
# - nok4 reactor side (addr 0x36)
# - zb0 (addr 0x37)
# - zb1 (addr 0x38)
#

devices = dict(
    nokbus1 = device('devices.vendor.ipc.IPCModBusTaco',
                      tacodevice = '//%s/test/network/ipcsms_1' % (nethost,),
                      loglevel = 'info',
                      lowlevel = True,
                      bustimeout = 0.5,
            ),
)
