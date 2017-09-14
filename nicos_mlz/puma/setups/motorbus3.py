description = 'Motor bus 3'
group = 'lowlevel'

devices = dict(
    motorbus3 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       # tacodevice = 'puma/rs485/moxa1_3',
                       tacodevice = 'puma/rs485/motorbus3',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
