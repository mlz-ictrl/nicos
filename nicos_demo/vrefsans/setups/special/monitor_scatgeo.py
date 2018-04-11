# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last modified 01.02.2018
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_scatgeo

description = 'REFSANS scattering geometry monitor'
group = 'special'

# Legende fuer _componentpositioncol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_componentpositioncol = Column(
    # Block(' x:  component position in beam direction (b3 = 0.0mm) ', [
    Block(' x:  component position in beam direction ', [
        BlockRow(
            Field(name='goniometer', dev='goniometer_x', width=14, unit='mm'),
            Field(name='sample center', dev='sample_x', width=14, unit='mm'),
            Field(name='monitor pos', dev='monitor_pos', width=14, unit='mm'),
            Field(name='backguard pos', dev='backguard_pos', width=14, unit='mm'),
            Field(name='tube pivot', dev='tube_pivot', width=10),
            Field(name='table origin', dev='table_zero', width=14, unit='mm'),
            Field(name='table', dev='table_pos', width=14, unit='mm'),
            Field(name='dist b3 gonio', dev='b3_gonio', width=14, unit='mm'),
            Field(name='dist b3 sample', dev='b3_sample', width=14, unit='mm'),
            Field(name='dist b3 monitor', dev='b3_monitor', width=14, unit='mm'),
            # Field(name='dist b3 backguard', dev='b3_backguard', width=14, unit='mm'),
            Field(name='det_pivot', dev='det_pivot', width=10),
            Field(name='det_table', dev='det_table', width=14, unit='mm'),
            Field(name='dist sample det', dev='sample_det', width=14, unit='mm'),
            Field(name='flight path', dev='flight_path', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _componentlateralcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_componentlateralcol = Column(
    Block(' y:  lateral component position and angle (b3 = 0.0mm) ', [
    # Block(' y:  lateral component position ', [
        BlockRow(
            Field(name='sample y', dev='probenwechsler', width=14, unit='mm'),
            Field(name='sample phi', dev='sample_phi', width=14, unit='deg'),
            Field(name='tube y', dev='tube_y', width=14, unit='mm'),
            Field(name='tube angle', dev='tube_lateral_angle', width=14, unit='deg'),
            Field(name='probenwechsler', dev='probenwechsler', width=14, unit='mm'),
            Field(name='gonio_y', dev='gonio_y', width=14, unit='mm'),
            Field(name='det y', dev='det_y', width=14, unit='mm'),
            Field(name='beamstop y', dev='beamstop_y', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _componentverticalcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_componentverticalcol = Column(
    Block(' z:  vertical component position and angle (b3 = 0.0mm) ', [
    # Block(' z:  vertical component position ', [
        BlockRow(
            Field(name='sample z', dev='sample_z', width=14, unit='mm'),
            Field(name='sample theta', dev='sample_theta', width=14, unit='deg'),
            Field(name='backguard', dev='backguard_z', width=14, unit='mm'),
            Field(name='tube', dev='tube_z', width=14, unit='mm'),
            Field(name='tube angle', dev='tube_vertical_angle', width=14, unit='deg'),
            Field(name='beamstop', dev='beamstop_z', width=14, unit='mm'),
            Field(name='gonio_z', dev='gonio_z', width=14, unit='mm'),
            Field(name='backguard', dev='backguard', width=14, unit='mm'),
            Field(name='det_yoke', dev='det_yoke', width=14, unit='mm'),
            Field(name='beamstop z', dev='beamstop_z', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _componentanglescol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_componentanglescol = Column(
    Block(' component angles ', [
        BlockRow(
            Field(name='gonio_theta', dev='gonio_theta', width=14, unit='deg'),
            Field(name='gonio_phi', dev='gonio_phi', width=14, unit='deg'),
            Field(name='gonio_omega', dev='gonio_omega', width=14, unit='deg'),
            Field(name='det hor angle', dev='det_hor_angle', width=14, unit='deg'),
            Field(name='det vert angle', dev='det_vert_angle', width=14, unit='deg'),
            Field(name='beam_tilt', dev='beam_tilt', width=14, unit='mrad'),
            ),
        ],
    ),
)


# Legende fuer _topgoniometercol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_topgoniometercol = Column(
    Block(' top goniometer ', [
        BlockRow(
            Field(name='top_theta', dev='top_theta', width=14, unit='deg'),
            Field(name='top_phi', dev='top_phi', width=14, unit='deg'),
            Field(name='top_omega', dev='top_omega', width=14, unit='deg'),
            Field(name='top_x', dev='top_x', width=14, unit='mm'),
            Field(name='top_y', dev='top_y', width=14, unit='mm'),
            Field(name='top_z', dev='top_z', width=14, unit='mm'),
            ),
        ],
    ),
)


# Legende fuer _autocollimatorcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_autocollimatorcol = Column(
    Block(' autocollimator ', [
        BlockRow(
            Field(name='ac_theta', dev='ac_theta', width=14, unit='deg'),
            Field(name='ac_phi', dev='ac_phi', width=14, unit='deg'),
            Field(name='ac_error', dev='ac_error', width=14, unit='deg'),
            ),
        ],
    ),
)


# Legende fuer _altimetercol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_altimetercol = Column(
    Block(' altimeter ', [
        BlockRow(
            Field(name='height', dev='altimeter', width=14, unit='mm'),
            ),
        ],
    ),
)


# Legende fuer _samplesizecol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_samplesizecol = Column(
    Block(' sample size ', [
        BlockRow(
            Field(name='length', dev='length', width=14, unit='mm'),
            Field(name='width', dev='width', width=14, unit='mm'),
            Field(name='footprint', dev='footprint', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _sampletempcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_sampletempcol = Column(
    Block(' sample temperature ', [
        BlockRow(
            Field(name='julabo', dev='temp_julabo', width=14, unit='deg C'),
            Field(name='cryo', dev='temp_cryo', width=14, unit='K'),
            ),
        ],
    ),
)

# Legende fuer _samplethumicol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices
_samplethumicol = Column(
    Block(' sample ', [
        BlockRow(
            Field(name='humidity', dev='humidity', width=14, unit='%'),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'localhost',
        valuefont = 'Consolas',
        padding = 5,
        layout = [
            Row(_componentpositioncol),
            Row(_componentlateralcol, _sampletempcol),
            Row(_componentverticalcol, _altimetercol, _samplethumicol),
            Row(_autocollimatorcol, _samplesizecol),
            Row(_componentanglescol),
            Row(_topgoniometercol),
        ],
    ),
)
