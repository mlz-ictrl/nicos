description = 'Motor bus 9'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus9 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa2_1' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus9' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
