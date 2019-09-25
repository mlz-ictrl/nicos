# coding: utf-8

description = 'Scattering Geometry, Experiment and Detector Monitor'
group = 'special'

_NLHcol = Column(
    Block('FRM-II and Guide Hall Information', [
        BlockRow(
            Field(name='Reactor Power', dev='ReactorPower', width=12, unit='(MW)'),
            Field(name='6-fold Shutter', dev='Sixfold', width=12),
            Field(name='Crane Position', dev='Crane', width=12, unit='(m)'),
            )
        ],
    ),
)

_Instrcol = Column(
    Block('Instrument Status', [
        BlockRow(
            Field(name='NL2b Guide', dev='NL2b', width=12),
            Field(name='Shutter', dev='shutter', width=12),
            Field(name=u'\u0263 Shutter', dev='shutter_gamma', width=12),
            ),
        BlockRow(
            Field(name='FAK40', dev='fak40', width=8),
            Field(name=u'T\u1d62\u2099', dev='t_memograph_in', width=12, unit=u'(\u2103)'),
            Field(name=u'T\u2092\u1d64\u209c', dev='t_memograph_out', width=12, unit=u'(\u2103)'),
            Field(name='Cooling Power', dev='cooling_memograph', width=12, unit='(kW)'),
            )
        ],
    ),
)

_experimentcol = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='User name', key='exp/username',    width=60, istext=True, maxlen=60),
            ),
        BlockRow(
            Field(name='Proposal title',    key='exp/title',    width=80, istext=True, maxlen=80),
            ),
        BlockRow(
            Field(name='Current Runnumber', key='exp/lastpoint'),
            Field(name='Counting Time', dev='timer', unit='(s)'),
            )
        ],
    ),
)



_probenort = Column(
    Block('Sample Information', [
        BlockRow(
            Field(name='Sample Name', key='sample/samplename', width=70,istext=True, maxlen=70),
            ),
        BlockRow(
            Field(name='Sample Width', key='sample/width', width=10, unit='(mm)'),
            Field(name='Sample Length', key='sample/length', width=10, unit='(mm)'),
            Field(name='Sample-Last Slit Distance', dev='d_last_slit_sample', width=10, format = '%.0f', unit='(mm)'),
            ),
        BlockRow(
            Field(name='First Slit',  key='primary_aperture/alias', width=10, istext=True, maxlen=3),
            Field(name='Last Slit',  key='last_aperture/alias', width=10, istext=True, maxlen=2),
            Field(name='Samplechanger', dev='samplechanger', width=10, unit='(mm)'),
            Field(name='Backguard',     dev='backguard', width=10, unit='(mm)'),
            ),
        ],
    ),
)



_biggonio = Column(
    Block('Goniometer Status', [
        BlockRow(
            Field(name=u'Angle \u03b8', dev='gonio_theta', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'Angle \u03c6', dev='gonio_phi', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'Angle \u03c9', dev='gonio_omega', width=7, format = '%.3f', unit='(deg)'),
            ),
        BlockRow(
            Field(name='z Pos', dev='gonio_z', width=7, format = '%.3f', unit='(mm)'),
            Field(name='y Pos', dev='gonio_y', width=7, format = '%.3f', unit='(mm)'),
            )
        ],
    ),
)

_topgonio = Column(
    Block('Top Goniometer Status', [
        BlockRow(
            Field(name=u'Angle \u03b8', dev='gonio_top_theta', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'Angle \u03c6', dev='gonio_top_phi', width=7, format = '%.3f', unit='(deg)'),
            ),
        BlockRow(
            Field(name='z Pos', dev='gonio_top_z', width=7, unit='(mm)'),
            )
        ],
    ),
)

_tempcol = Column(
    Block('Thermostats Status', [
        BlockRow(
            Field(name='Julabo', dev='temp_julabo', width=14, unit=u'(\u2103)'),
            Field(name='Cryostat', dev='temp_cryo', width=14, unit='(K)'),
            )
        ],
    ),
)

_flipper = Column(
    Block('Spin Flipper', [
        BlockRow(
            Field(dev='frequency', width=7, unit='(kHz)'),
            Field(dev='current', width=7, unit='(A)'),
            Field(dev='flipper', name='Flipping_State', width=7),
            ),
        ],
    ),
)

_justierung = Column(
    Block('Aligment Devices Status', [
        BlockRow(
            Field(name=u'Autocoll. Angle \u03b8', dev='autocollimator_theta', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'Autocoll. Angle \u03c6', dev='autocollimator_phi', width=7, format = '%.3f', unit='(deg)'),
            ),
        BlockRow(
            Field(name='Altimeter', dev='height', width=7, unit='mm'),
            ),
        ],
    ),
)

_detector = Column(
    Block('Detector Information', [
        BlockRow(
            Field(name='Table', dev='det_table', width=10, format = '%.0f', unit='(mm)'),
            Field(name='Yoke', dev='det_yoke', width=10, format = '%.0f', unit='(mm)'),
            Field(name='Pivot', dev='det_pivot', width=10),
            ),
        BlockRow(
            Field(name='Counting Rate', dev='detector_count_rate', width=10, unit='(Hz)'),
            Field(name='Integral counts', dev='image', width=15),
            ),
        ],
    ),
)


_monitor = Column(
    Block('Monitor Information', [
        BlockRow(
            Field(name='Monitor 1', key='mon1', width=10),
            Field(name='Monitor 2', dev='mon2', width=10),
            ),
        ],
    ),
)


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_NLHcol, _Instrcol),
            Row(_experimentcol, _probenort),
            Row(_tempcol, _flipper),
            Row(_biggonio, _topgonio, _justierung),
            Row(_detector, _monitor)
        ],
    ),
)
