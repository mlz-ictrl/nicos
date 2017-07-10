description = 'Motor bus 1'
group = 'lowlevel'

devices = dict(
    motorbus1 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa1_1',
                       bustimeout = 1.0,
                       lowlevel = True,
                      ),
)
