description = 'Motor bus 6'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus6 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        tacodevice = '//%s/puma/rs485/moxa3_1' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),

# motorbus for slit1 (old motorbus6)
    motorbus6a = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        # tacodevice = '//%s/puma/rs485/moxa1_6' % nethost,
        tacodevice = '//%s/puma/rs485/motorbus6a' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
