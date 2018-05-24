description = 'IPC Motor bus device configuration'

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2:10000/test/'

# data from instrument.inf
# used for:
# - nok4 reactor side (addr 0x36)
# - zb0 (addr 0x37)
# - zb1 (addr 0x38)
#

devices = dict(
    nokbus2 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'ipcsms_b/bio',
       lowlevel = True,
    ),
)
