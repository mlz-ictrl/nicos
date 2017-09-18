description = 'Motor bus 11'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus11 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        tacodevice = '//%s/puma/rs485/st' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
