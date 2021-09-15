description = 'Switches for diom modules'

tango_base = configdata('localconfig.tango_base')

devices = dict(
    diom1 = device('nicos.devices.entangle.DigitalInput',
                   description = 'DIOM PhyMotion module 1',
                   tangodevice = tango_base + 'device/PhyMOTION/diom1',
                   fmtstr = '%#x',
                   lowlevel = True,
                   ),

    diom2 = device('nicos.devices.entangle.DigitalInput',
                   description = 'DIOM PhyMotion module 2',
                   tangodevice = tango_base + 'device/PhyMOTION/diom2',
                   fmtstr = '%#x',
                   lowlevel = True,
                   ),
)
