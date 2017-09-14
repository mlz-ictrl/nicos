description = 'Motor bus 3'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus3 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_3' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus3' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
