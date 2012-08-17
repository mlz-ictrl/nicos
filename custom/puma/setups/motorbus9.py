description = 'Motor bus 9'
group = 'lowlevel'

devices = dict(
    motorbus9 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/3',
                       timeout = 0.5,
                       ),
)
