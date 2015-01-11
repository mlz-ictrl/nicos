description = 'Motor bus 5'
group = 'lowlevel'

devices = dict(
    motorbus5 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s21',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
