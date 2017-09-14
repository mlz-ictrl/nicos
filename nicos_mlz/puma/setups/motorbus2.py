description = 'Motor bus 2'
group = 'lowlevel'

devices = dict(
    motorbus2 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       # tacodevice = 'puma/rs485/moxa1_2',
                       tacodevice = 'puma/rs485/motorbus2',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
