description = 'Motor bus 13'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus13 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        tacodevice = '//%s/puma/rs485/motorbus13' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
