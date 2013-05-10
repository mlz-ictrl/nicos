description = 'Motor bus 6'
group = 'lowlevel'

devices = dict(
    motorbus6 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s22',
                       bustimeout = 0.1,
                       lowlevel = True,
                       ),
)
