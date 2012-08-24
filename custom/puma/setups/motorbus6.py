description = 'Motor bus 6'
group = 'lowlevel'

devices = dict(
    motorbus6 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s22',
                       timeout = 0.5,
                       ),
)
