description = 'Motor bus 8'
group = 'lowlevel'

devices = dict(
    motorbus8 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/io',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
