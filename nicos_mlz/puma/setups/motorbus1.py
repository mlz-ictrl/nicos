description = 'Motor bus 1'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus1 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_1' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus1' % nethost,
        bustimeout = 1.0,
        lowlevel = True,
    ),
)
