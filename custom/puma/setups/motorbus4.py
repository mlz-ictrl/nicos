description = 'Motor bus 4'
group = 'lowlevel'

devices = dict(
    motorbus4 = device('nicos.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s43',
                       timeout = 0.5,
                       ),
)
