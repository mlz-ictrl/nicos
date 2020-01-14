description = 'IPC Motor bus device configuration'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']

devices = dict(
    nokbus3 = device('nicos.devices.vendor.ipc.IPCModBusTango',
       tangodevice = tango_base + 'test/ipcsms_c/bio',
       lowlevel = True,
    ),
)
