# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last modified 01.02.2018
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_scatgeo

description = 'scattering geometry'
group = 'special'


_componentpositioncol = Column(
    # Block(' x:  component position in beam direction (b3 = 0.0mm) ', [
    Block(' x:  component position in beam direction ', [
        BlockRow(
            Field(name='goniometer', dev='goniometer_x', width=14, unit='mm'),
            Field(name='sample center', dev='sample_x', width=14, unit='mm'),
            Field(name='monitor pos', dev='monitor_pos', width=14, unit='mm'),
            Field(name='backguard pos', dev='backguard', width=14, unit='mm'),
            #Field(name='table origin', dev='table_zero', width=14, unit='mm'),
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

_componentlateralcol = Column(
    Block(' y:  lateral component position and angle (b3 = 0.0mm) ', [
    # Block(' y:  lateral component position ', [
        BlockRow(
            Field(name='sample y', dev='gonio_y', width=14, unit='mm'),
            Field(name='sample phi', dev='gonio_phi', width=14, unit='deg'),
            #Field(name='tube y', dev='tube_y', width=14, unit='mm'),
            #Field(name='tube angle', dev='tube_lateral_angle', width=14, unit='deg'),
            Field(name='samplechanger', dev='samplechanger', width=14, unit='mm'),
            Field(name='gonio_y', dev='gonio_y', width=14, unit='mm'),
            ),
        ],
    ),
)

_componentverticalcol = Column(
    Block(' z:  vertical component position and angle (b3 = 0.0mm) ', [
    # Block(' z:  vertical component position ', [
        BlockRow(
            Field(name='sample z', dev='gonio_z', width=14, unit='mm'),
            Field(name='sample theta', dev='gonio_theta', width=14, unit='deg'),
            Field(name='backguard', dev='backguard', width=14, unit='mm'),
            Field(name='tube', dev='det_tube', width=14, unit='mm'),
            #Field(name='tube angle', dev='tube_vertical_angle', width=14, unit='deg'),
            #Field(name='beamstop', dev='beamstop_z', width=14, unit='mm'),
            Field(name='gonio_z', dev='gonio_z', width=14, unit='mm'),
            Field(name='backguard', dev='backguard', width=14, unit='mm'),
            Field(name='det_yoke', dev='det_yoke', width=14, unit='mm'),
            ),
        ],
    ),
)

_componentanglescol = Column(
    Block(' component angles ', [
        BlockRow(
            Field(name='gonio_theta', dev='gonio_theta', width=14, unit='deg'),
            Field(name='gonio_phi', dev='gonio_phi', width=14, unit='deg'),
            Field(name='gonio_omega', dev='gonio_omega', width=14, unit='deg'),
            #Field(name='det hor angle', dev='det_hor_angle', width=14, unit='deg'),
            #Field(name='det vert angle', dev='det_vert_angle', width=14, unit='deg'),
            #Field(name='beam_tilt', dev='beam_tilt', width=14, unit='mrad'),
            ),
        ],
    ),
)


_topgoniometercol = Column(
    Block(' top goniometer ', [
        BlockRow(
            Field(name='top_theta', dev='gonio_top_theta', width=14, unit='deg'),
            Field(name='top_phi', dev='gonio_top_phi', width=14, unit='deg'),
            #Field(name='top_omega', dev='top_omega', width=14, unit='deg'),
            #Field(name='top_x', dev='top_x', width=14, unit='mm'),
            #Field(name='top_y', dev='top_y', width=14, unit='mm'),
            Field(name='top_z', dev='gonio_top_z', width=14, unit='mm'),
            ),
        ],
    ),
)


_autocollimatorcol = Column(
    Block(' autocollimator ', [
        BlockRow(
            Field(name='theta', dev='autocollimator_theta', width=14, unit='deg'),
            Field(name='phi', dev='autocollimator_phi', width=14, unit='deg'),
            #Field(name='ac_error', dev='autocollimator_error', width=14, unit='deg'),
            ),
        ],
    ),
)


_altimetercol = Column(
    Block(' altimeter ', [
        BlockRow(
            Field(name='height', dev='height', width=14, unit='mm'),
            ),
        ],
    ),
)


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

_sampletempcol = Column(
    Block(' sample temperature ', [
        BlockRow(
            Field(name='julabo', dev='temp_julabo', width=14, unit='deg C'),
            Field(name='cryo', dev='temp_cryo', width=14, unit='K'),
            ),
        ],
    ),
)

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
        cache = 'refsanssw.refsans.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
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
