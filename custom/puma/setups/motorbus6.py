description = 'Motor bus 6'
group = 'lowlevel'

devices = dict(
    motorbus6 = device('devices.vendor.ipc.IPCModBusTaco',
#                       tacodevice = 'puma/rs485/s22',
                       tacodevice = 'puma/rs485/moxa3_1',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
