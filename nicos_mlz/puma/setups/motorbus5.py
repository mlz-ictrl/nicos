description = 'Motor bus 5'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus5 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_5' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus5' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
