description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

tango_base = 'tango://miractrl.mira.frm2:10000/mira/'

devices = dict(
    temp_volt = device('nicos.devices.tango.PowerSupply',
                  description = 'current in first channel of supply (flipper current)',
                  tangodevice = tango_base + 'tti2/out1volt',
                  lowlevel = True,
                  timeout = 5,
                  precision = 0.2,
                 ),
    temp_switch = device('nicos.devices.generic.MultiSwitcher',
                   description = 'Spin flipper switch',
                   moveables = ['temp_volt'],
                   precision = [0.2],
                   mapping = {1: [16], 0: [0]},
                  ),
)
