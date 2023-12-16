description = 'Motor bus 5'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2.tum.de:10000/puma/'

devices = dict(
    motorbus5 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus5/bio',
       visibility = (),
    ),
)
