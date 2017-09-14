description = 'Motor bus coder for mtt, mth'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus14 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa2_6' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus14' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
