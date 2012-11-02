description = 'Motor bus 9'
group = 'lowlevel'

devices = dict(
    motorbus9 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/3',
                       timeout = 0.5,
                       ),
)
