description = 'Motor bus 13'

group = 'lowlevel'

tango_base = 'tango://pumadma.puma.frm2:10000/puma/'

devices = dict(
    motorbus13 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'motorbus13/bio',
       lowlevel = True,
    ),
)
