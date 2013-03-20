#  -*- coding: utf-8 -*-

description = 'setup for sample attenuator'

includes = []

devices = dict(
<<<<<<< HEAD
=======

        #~ wut = device('panda.wechsler.Beckhoff',
                #~ host='sat-box.panda.frm2',
                #~ addr=1,
                #~ lowlevel=True,
                #~ ),
        #~ sat = device('panda.satbox.SatBox',
                #~ bus='wut',
                #~ fmtstr='%d',
                #~ unit='mm'),
>>>>>>> PANDA: Move sat to a modbus-taco-server
    sat = device('panda.satbox.SatBox',
                  tacodevice = 'panda/modbus/sat',
                  unit = 'mm',
                  fmtstr = '%d',
<<<<<<< HEAD
                  #~ blades = [1, 2, 5, 10, 20],
                  blades = [0, 2, 5, 10, 20], # blade gets stuck until repair -> disable it here
                  slave_addr = 1, # WUT
=======
                  blades = [1, 2, 5, 10, 20],
                  slave_addr = 1, #WUT
>>>>>>> PANDA: Move sat to a modbus-taco-server
                  addr_out = 0x1020,
                  addr_in = 0x1000,
                  ),
)

startupcode="""
<<<<<<< HEAD
printwarning('Disabling 1mm blade of sat as it gets stuck until repair....')
=======
printwarning('Disabling 1mm blade of sat as it gets stuck...')
>>>>>>> PANDA: Move sat to a modbus-taco-server
sat.blades[0]=0
"""

