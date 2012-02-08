#  -*- coding: utf-8 -*-

description = 'setup for sample attenuator'

includes = []

#sysconfig = {'cache': None} # disables Cache completely

devices = dict(
            
        wut = device('nicos.panda.wechsler.Beckhoff',
                host='sat-box.panda.frm2',
        		addr=1,
                lowlevel=True,
                ),
        sat = device('nicos.panda.satbox.SatBox',
                bus='wut',
                fmtstr='%d',
                unit='mm'),
)

