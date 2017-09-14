description = 'Motor bus Analyser'

group = 'lowlevel'

nethost = 'pumasrv.puma.frm2'

devices = dict(
    motorbus12 = device('nicos.devices.vendor.ipc.IPCModBusTaco',
        tacodevice = '//%s/puma/rs485/moxa3_1' % nethost,
        bustimeout = 0.1,
        lowlevel = True,
    ),
)
