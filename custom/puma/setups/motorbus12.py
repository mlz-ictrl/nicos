description = 'Motor bus Analyser'
group = 'lowlevel'

devices = dict(
    motorbus12 = device('devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa3_1',
                       bustimeout = 0.1,
                       lowlevel = True,
                       ),
)
