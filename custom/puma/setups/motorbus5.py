description = 'Motor bus 5'
group = 'lowlevel'

devices = dict(
    motorbus5 = device('nicos.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s21',
                       timeout = 0.5,
                       ),
)
