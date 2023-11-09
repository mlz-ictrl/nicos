description = 'Bus device to IPC motor cards'

group = 'lowlevel'

tango_host = 'localhost'

tango_base = f'tango://{tango_host}:10000/erwin/motorbus/'

devices = dict(
    motorbus = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'io',
       visibility = (),
    ),
)
