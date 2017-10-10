description = 'Motor bus 10'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus10 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa2_5' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus10' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
