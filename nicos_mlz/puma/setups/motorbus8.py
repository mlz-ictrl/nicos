description = 'Motor bus 8'
group = 'lowlevel'

devices = dict(
    motorbus8 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa1_8',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
