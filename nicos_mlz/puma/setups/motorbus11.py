description = 'Motor bus 11'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2:10000/puma/'

devices = dict(
    motorbus11 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus11/bio',
       lowlevel = True,
    ),
)
