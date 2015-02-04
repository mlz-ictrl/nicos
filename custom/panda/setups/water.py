#  -*- coding: utf-8 -*-

description = 'setup for water flow'

includes = []

group = 'optional'

devices = dict(
    water = device('panda.compbox.WaterControlBox',
                   description = 'Water flux readout',
                   tacodevice = 'panda/modbus/compressor',
                   fmtstr = '%s',
                   slave_addr = 1, # WUT
                   addr_in = 0x1001,
                  ),
)
