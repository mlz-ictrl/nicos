#  -*- coding: utf-8 -*-

description = 'setup for sample attenuator'

includes = []

group = 'optional'

devices = dict(
    sat = device('panda.satbox.SatBox',
                 description = 'Sample beam attenuator',
                 tacodevice = 'panda/modbus/sat',
                 unit = 'mm',
                 fmtstr = '%d',
              #~ blades = [1, 2, 5, 10, 20],
                 blades = [0, 2, 5, 10, 20], # blade gets stuck until repair -> disable it here
                 slave_addr = 1, # WUT
                 addr_out = 0x1020,
              #~ addr_in = 0x1000, #not yet used, see code in custom/panda/lib/satbox
                ),
)

startupcode = """
printwarning('Disabled 1mm blade of sat as it gets stuck until repair....')
"""
