description = 'Motor bus 4'
group = 'lowlevel'

devices = dict(
    motorbus4 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s43',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
