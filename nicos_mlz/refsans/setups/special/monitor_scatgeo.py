# created by Martin Haese, Tel FRM 10763
# last modified 30.10.2017
# to call it
# ssh refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_scatgeo

description = 'REFSANS scattering geometry monitor'
group = 'special'

# Legende fuer _componentpositioncol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_componentpositioncol = Column(
    Block(' x:  component position in beam direction (b3 = 0.0mm) ', [
        BlockRow(
            Field(name='goniometer', dev='goniometer_x', width=14, unit='mm'),
            Field(name='sample center', dev='sample_x', width=14, unit='mm'),
            Field(name='monitor pos', dev='monitor_pos', width=14, unit='mm'),
            Field(name='backguard pos', dev='backguard_pos', width=14, unit='mm'),
            Field(name='tube pivot', dev='tube_pivot', width=10),
            Field(name='table origin', dev='table_zero', width=14, unit='mm'),
            Field(name='table', dev='table_pos', width=14, unit='mm'),
            Field(name='flight path', dev='flight_path', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _componentlateralcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_componentlateralcol = Column(
    Block(' y:  lateral component position and angle (b3 = 0.0mm) ', [
        BlockRow(
            Field(name='sample y', dev='probenwechsler', width=14, unit='mm'),
            Field(name='sample phi', dev='sample_phi', width=14, unit='deg'),
            Field(name='tube y', dev='tube_y', width=14, unit='mm'),
            Field(name='tube angle', dev='tube_lateral_angle', width=14, unit='deg'),
            Field(name='beamstop y', dev='beamstop_y', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _componentverticalcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_componentverticalcol = Column(
    Block(' z:  vertical component position and angle (b3 = 0.0mm) ', [
        BlockRow(
            Field(name='sample z', dev='sample_z', width=14, unit='mm'),
            Field(name='sample theta', dev='sample_theta', width=14, unit='deg'),
            Field(name='backguard', dev='backguard_z', width=14, unit='mm'),
            Field(name='tube', dev='tube_z', width=14, unit='mm'),
            Field(name='tube angle', dev='tube_vertical_angle', width=14, unit='deg'),
            Field(name='beamstop', dev='beamstop_z', width=14, unit='mm'),
            ),
        ],
    ),
)


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl01.refsans.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_componentpositioncol),
            Row(_componentlateralcol),
            Row(_componentverticalcol),
        ],
    ),
)
