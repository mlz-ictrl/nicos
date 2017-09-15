description = 'Motor bus 4'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus4 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_4' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus4' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
