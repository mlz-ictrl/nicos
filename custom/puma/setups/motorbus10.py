description = 'Motor bus 10'
group = 'lowlevel'

devices = dict(
    motorbus10 = device('devices.vendor.ipc.IPCModBusTaco',
                        tacodevice = 'puma/rs485/1',     # WARNING: There is no such tacodevice!
                        bustimeout = 0.1,
                        lowlevel = True,
                       ),
)
