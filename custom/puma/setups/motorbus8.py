description = 'Motor bus 8'
group = 'lowlevel'

devices = dict(
    motorbus8 = device('nicos.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/io',
                       timeout = 0.5,
                       ),
)
