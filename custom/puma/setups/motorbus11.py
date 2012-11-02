description = 'Motor bus 11'
group = 'lowlevel'

devices = dict(
    motorbus11 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/st',
                       timeout = 0.5,
                       ),
)
