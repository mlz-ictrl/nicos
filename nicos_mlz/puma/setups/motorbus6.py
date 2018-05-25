description = 'Motor bus 6'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2:10000/puma/'

devices = dict(
    motorbus6 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus6/bio',
       lowlevel = True,
    ),
    motorbus6a = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus6a/bio',
       lowlevel = True,
    ),
)
