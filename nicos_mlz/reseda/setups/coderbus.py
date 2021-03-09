description = 'Coder bus'

group = 'lowlevel'

tango_base = 'tango://resedahw2.reseda.frm2.tum.de:10000/reseda/'

devices = dict(
    encoderbus = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'rs485/coder_bio',
       lowlevel = True,
    ),
)
