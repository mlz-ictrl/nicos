description = 'Motor bus 3'
group = 'lowlevel'

devices = dict(
    motorbus3 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s42',
                       timeout = 0.5,
                       ),
)
