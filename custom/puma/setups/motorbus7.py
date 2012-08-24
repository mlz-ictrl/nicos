description = 'Motor bus 7'
group = 'lowlevel'

devices = dict(
    motorbus7 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s23',
                       timeout = 0.5,
                       ),
)
