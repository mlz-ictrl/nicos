description = 'Motor bus 8'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2:10000/puma/'

devices = dict(
    motorbus8 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus8/bio',
       lowlevel = True,
    ),
)
