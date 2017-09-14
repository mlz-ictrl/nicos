description = 'Motor bus 4'
group = 'lowlevel'

devices = dict(
    motorbus4 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       # tacodevice = 'puma/rs485/moxa1_4',
                       tacodevice = 'puma/rs485/motorbus4',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
