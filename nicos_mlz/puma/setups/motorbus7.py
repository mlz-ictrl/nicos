description = 'Motor bus 7'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus7 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_7' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus7' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
