description = 'Motor bus 7'
group = 'lowlevel'

devices = dict(
    motorbus7 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa1_7',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
