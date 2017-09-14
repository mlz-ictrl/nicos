description = 'Motor bus 6'
group = 'lowlevel'

devices = dict(
    motorbus6 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                       tacodevice = 'puma/rs485/moxa3_1',
                       bustimeout = 0.1,
                       lowlevel = True,
                      ),

# motorbus for slit1 (old motorbus6)
    motorbus6a = device('nicos.devices.vendor.ipc.IPCModBusTaco',
                        tacodevice = 'puma/rs485/moxa1_6',
                        # tacodevice = 'puma/rs485/motorbus6a',
                        bustimeout = 0.1,
                        lowlevel = True,
                       ),
)
