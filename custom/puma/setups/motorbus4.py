description = 'Motor bus 4'
group = 'lowlevel'

devices = dict(
    motorbus4 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa1_4',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
