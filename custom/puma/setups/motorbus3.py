description = 'Motor bus 3'
group = 'lowlevel'

devices = dict(
    motorbus3 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa1_3',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
