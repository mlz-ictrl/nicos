description = 'Motor bus 8'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus8 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        tacodevice = '//%s/puma/rs485/moxa1_8' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
