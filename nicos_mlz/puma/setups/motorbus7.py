description = 'Motor bus 7'

group = 'lowlevel'

tango_base = 'tango://puma5.puma.frm2:10000/puma/'

devices = dict(
    motorbus7 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus7/bio',
       lowlevel = True,
    ),
)
