# -*- coding: utf-8 -*-

description = 'ANTARES switchable sockets'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict()

for n in range(1, 16):  # from 01 to 15
    devices['socket%02d' % n] = \
        device('nicos.devices.entangle.NamedDigitalOutput',
               description = 'Powersocket %02d' % n,
               tangodevice = tango_base + 'fzjdp_digital/Socket%02d' % n,
               mapping = dict(on=1, off=0),
               unit = '',
              )

monitor_blocks = dict(
    cabinet1 = Block('Sockets Cabinet 1',
        [
            BlockRow(
                Field(dev='socket01', width=9),
                Field(dev='socket02', width=9),
                Field(dev='socket03', width=9),
            ),
        ],
        setups=setupname,
    ),
    cabinet2 = Block('Sockets Cabinet 2',
        [
            BlockRow(
                Field(dev='socket04', width=9),
                Field(dev='socket05', width=9),
                Field(dev='socket06', width=9),
            ),
        ],
        setups=setupname,
    ),
    cabinet3 = Block('Sockets Cabinet 3',
        [
            BlockRow(
                Field(dev='socket07', width=9),
                Field(dev='socket08', width=9),
                Field(dev='socket09', width=9),
            ),
        ],
        setups=setupname,
    ),
    cabinet6 = Block('Sockets Cabinet 6',
        [
            BlockRow(
                Field(dev='socket10', width=9),
                Field(dev='socket11', width=9),
                Field(dev='socket12', width=9),
            ),
        ],
        setups=setupname,
    ),
    cabinet7 = Block('Sockets Cabinet 7',
        [
            BlockRow(
                Field(dev='socket13', width=9),
                Field(dev='socket14', width=9),
                Field(dev='socket15', width=9),
            ),
        ],
        setups=setupname,
    ),
)
