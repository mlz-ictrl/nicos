description = 'Motor bus 10'
group = 'lowlevel'

devices = dict(
    motorbus10 = device('nicos.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/1',
                       timeout = 0.5,
                       ),
)
