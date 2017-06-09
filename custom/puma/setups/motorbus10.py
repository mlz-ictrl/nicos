description = 'Motor bus 10'

group = 'lowlevel'

devices = dict(
    motorbus10 = device('devices.vendor.ipc.IPCModBusTaco',
        tacodevice = 'puma/rs485/moxa2_5',
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
