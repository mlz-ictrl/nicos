description = 'He3 cell inserter devices'

group = 'optional'

includes = ['motorbus6']

devices = dict(
    he_cell_top = device('nicos.devices.vendor.ipc.Input',
        description = 'Top position of He-cell: out of the beam',
        bus = 'motorbus6',
        addr = 111,
        first = 15,
        last = 15,
        lowlevel = True,
        unit = ''
    ),
    he_cell_bottom = device('nicos.devices.vendor.ipc.Input',
        description = 'Bottom position of He-cell: in the beam',
        bus = 'motorbus6',
        addr = 111,
        first = 14,
        last = 14,
        lowlevel = True,
        unit = ''
    ),
    he_cell_sw = device('nicos.devices.vendor.ipc.Output',
        description = 'He cell lift',
        bus = 'motorbus6',
        addr = 103,
        first = 5,
        last = 5,
        lowlevel = True,
        unit = ''
    ),
    he_cell_lift = device('nicos_mlz.puma.devices.hecell.HeCellLifter',
        description = 'He cell',
        moveables = ['he_cell_sw'],
        readables = ['he_cell_bottom', 'he_cell_top'],
        precision = None,
        mapping = {
            'in': [0, 1, 0],
            'out': [1, 0, 1],
        },
        fallback = 'moving',
        timeout = 10,
    ),
)
