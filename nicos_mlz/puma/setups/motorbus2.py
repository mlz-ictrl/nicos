description = 'Motor bus 2'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus2 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_2' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus2' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
