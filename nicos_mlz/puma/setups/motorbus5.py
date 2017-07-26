description = 'Motor bus 5'
group = 'lowlevel'

devices = dict(
    motorbus5 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa1_5',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),
)
