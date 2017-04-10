description = 'Motor bus coder for mtt, mth'
group = 'lowlevel'

devices = dict(
    motorbus14 = device('devices.vendor.ipc.IPCModBusTaco',
                        tacodevice = 'puma/rs485/moxa2_6',
                        bustimeout = 0.1,
                        lowlevel = True,
                       ),
)
