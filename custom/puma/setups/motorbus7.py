description = 'Motor bus 7'
group = 'lowlevel'

devices = dict(
    motorbus7 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/s23',
                       tacotimeout = 0.5,
                       lowlevel = True,
                       ),
)
