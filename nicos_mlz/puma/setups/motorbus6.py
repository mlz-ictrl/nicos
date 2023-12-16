description = 'Motor bus 6'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2.tum.de:10000/puma/'

devices = dict(
    motorbus6 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus6/bio',
       visibility = (),
    ),
    motorbus6a = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus6a/bio',
       visibility = (),
    ),
)
