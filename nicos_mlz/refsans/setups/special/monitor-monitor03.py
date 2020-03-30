# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last version by Gaetano Mangiapia, Tel 54839 on Jan 09th 2020

# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_chopper

description = 'Scattering Geometry, Experiment and Detector [Monitor 03]'
group = 'special'

_NLHcol = Column(
    Block('FRM-II and Guide Hall Information', [
        BlockRow(
            Field(name='reactor power', dev='ReactorPower', width=10, format = '%.1f', unit='(MW)'),
            Field(name='6-fold shutter', dev='Sixfold', width=10),
            Field(name='crane position', dev='Crane', width=10, format = '%.1f', unit='(m)'),
            )
        ],
    ),
)

_Instrcol = Column(
    Block('Instrument Status', [
        BlockRow(
            Field(name='NL2b Guide', dev='NL2b', width=10),
            Field(name='shutter', dev='shutter', width=10),
            Field(name=u'\u0263 shutter', dev='shutter_gamma', width=10),
            ),
        BlockRow(
            Field(name='FAK40 capacity', dev='FAK40_Cap', width=10, format = '%.1f', unit='(l)' ),
            Field(name='FAK40 pressure', dev='FAK40_Press', width=10, format = '%.3f', unit='(bar)'),
            Field(name=u'T\u1d62\u2099', dev='t_memograph_in', width=10, format = '%.1f', unit=u'(\u2103)'),
            Field(name=u'T\u2092\u1d64\u209c', dev='t_memograph_out', format = '%.1f', width=10, unit=u'(\u2103)'),
            Field(name='cooling power', dev='cooling_memograph', format = '%.1f', width=10, unit='(kW)'),
            )
        ],
    ),
)

_experimentcol = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='proposal', key='exp/proposal', width=7),
            Field(name='user(s)', key='exp/users',    width=60, istext=True, maxlen=60),
            ),
        BlockRow(
            Field(name='proposal title',    key='exp/title',    width=80, istext=True, maxlen=80),
            ),
        BlockRow(
            Field(name='current runnumber', key='exp/lastpoint'),
            Field(name='counting time', dev='timer', unit='(s)'),
            )
        ],
    ),
)



_probenort = Column(
    Block('Sample Information', [
        BlockRow(
            Field(name='sample name', key='sample/samplename', width=70,istext=True, maxlen=70),
            ),
        BlockRow(
            Field(name='sample width', key='Sample/width', width=10, format = '%.0f', unit='(mm)'),
            Field(name='sample length', key='Sample/length', width=10, format = '%.0f', unit='(mm)'),
            Field(name='sample-last slit distance', dev='d_last_slit_sample', width=10, format = '%.0f', unit='(mm)'),
            ),
        BlockRow(
            Field(name='first slit',  key='primary_aperture/alias', width=10, istext=True, maxlen=3),
            Field(name='last slit',  key='last_aperture/alias', width=10, istext=True, maxlen=2),
            Field(name='samplechanger', dev='samplechanger', width=10, format = '%.1f', unit='(mm)'),
            Field(name='backguard',     dev='backguard', width=10, format = '%.1f', unit='(mm)'),
            ),
        ],
    ),
)



_biggonio = Column(
    Block('Goniometer Status', [
        BlockRow(
            Field(name=u'angle \u03b8', dev='gonio_theta', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'angle \u03c6', dev='gonio_phi', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'angle \u03c9', dev='gonio_omega', width=7, format = '%.3f', unit='(deg)'),
            ),
        BlockRow(
            Field(name='vertical position', dev='gonio_z', width=7, format = '%.1f', unit='(mm)'),
            Field(name='lateral position', dev='gonio_y', width=7, format = '%.1f', unit='(mm)'),
            )
        ],
    ),
)

_topgonio = Column(
    Block('Top Goniometer Status', [
        BlockRow(
            Field(name=u'angle \u03b8', dev='gonio_top_theta', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'angle \u03c6', dev='gonio_top_phi', width=7, format = '%.3f', unit='(deg)'),
            ),
        BlockRow(
            Field(name='vertical position', dev='gonio_top_z', width=7, format = '%.3f', unit='(mm)'),
            )
        ],
    ),
)

#_tempcol = Column(
#    Block('Thermostats Status', [
#        BlockRow(
#            Field(name='Julabo', dev='temp_julabo', width=14, unit=u'(\u2103)'),
#            Field(name='Cryostat', dev='temp_cryo', width=14, unit='(K)'),
#            )
#        ],
#    ),
#)

#_flipper = Column(
#    Block('Spin Flipper', [
#        BlockRow(
#            Field(dev='frequency', width=7, unit='(kHz)'),
#            Field(dev='current', width=7, unit='(A)'),
#            Field(dev='flipper', name='Flipping_State', width=7),
#            ),
#        ],
#    ),
#)

_justierung = Column(
    Block('Aligment Devices Status', [
        BlockRow(
            Field(name=u'autocollimator angle \u03b8', dev='autocollimator_theta', width=7, format = '%.3f', unit='(deg)'),
            Field(name=u'autocollimator angle \u03c6', dev='autocollimator_phi', width=7, format = '%.3f', unit='(deg)'),
            ),
        BlockRow(
            Field(name='altimeter', dev='height', width=7, unit='(mm)'),
            ),
        ],
    ),
)

_detector = Column(
    Block('Detector Information', [
        BlockRow(
            Field(name='table', dev='det_table', width=10, format = '%.0f', unit='(mm)'),
            Field(name='yoke', dev='det_yoke', width=10, format = '%.0f', unit='(mm)'),
            Field(name='pivot', dev='det_pivot', width=10),
            ),
        BlockRow(
            Field(name='counting rate', dev='detector_count_rate', width=10, format = '%.1f', unit='(Hz)'),
            Field(name='integral counts', dev='image', format = '%.0f', width=10),
            Field(name='safe detector system', dev='sds', width=10, format = '%.1f', unit='(Hz)'),
            ),
        ],
    ),
)


_monitor = Column(
    Block('Monitor Information', [
        BlockRow(
            Field(name='monitor 1', key='mon1', width=10),
            Field(name='monitor 2', dev='mon2', width=10),
            Field(name='monitor number', dev='prim_monitor_typ', width=10),
            ),
        BlockRow(
            Field(name='monitor-last slit distance', dev='prim_monitor_x', width=10, format = '%.0f', unit='(mm)'),
            ),
        ],
    ),
)


_dettube = Column(
    Block(' Detector Tube Status', [
        BlockRow(
            Field(widget='nicos_mlz.refsans.gui.monitorwidgets.RefsansWidget', width=50, height=40,
                  pivot='det_pivot', detpos='det_table', tubeangle='tube_angle'),
            ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl01.refsans.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_NLHcol, _Instrcol),
            Row(_experimentcol, _probenort),
            #Row(_tempcol, _flipper),
            Row(_biggonio, _topgonio, _justierung),
            Row(_detector, _monitor),
            Row(_dettube)
        ],
    ),
)
