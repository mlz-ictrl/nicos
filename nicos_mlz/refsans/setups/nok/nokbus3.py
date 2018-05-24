description = 'IPC Motor bus device configuration'

group = 'lowlevel'

tango_base = 'tango://refsanshw.refsans.frm2:10000/test/'

devices = dict(
    nokbus3 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'ipcsms_c/bio',
       lowlevel = True,
    ),
)
