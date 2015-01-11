description = 'Motor bus 9'
group = 'lowlevel'

devices = dict(
    motorbus9 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/3',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
