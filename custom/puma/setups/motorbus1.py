description = 'Motor bus 1'
group = 'lowlevel'

devices = dict(
    motorbus1 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/mc',
                       timeout = 0.5,
                       ),
)
