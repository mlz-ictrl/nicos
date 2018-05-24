description = 'IPC Motor bus device configuration'

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2:10000/test/'

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
    nokbus1 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'ipcsms_a/bio',
       lowlevel = True,
    ),
)
