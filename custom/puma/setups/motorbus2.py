description = 'Motor bus 2'
group = 'lowlevel'

devices = dict(
    motorbus2 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s41',
                       timeout = 0.5,
                       ),
)
