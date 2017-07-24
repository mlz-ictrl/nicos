# created by Martin Haese, Tel FRM 10763
# last modified 21.07.2017
# to call it
# ssh refsans@refsansctrl02 oder 01
# cd /refsanscontrol
# ./bin/nicos-monitor -S monitor_detector

description = 'REFSANS detector monitor'
group = 'special'

# Legende fuer _detconfigcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_detconfigcol = Column(
    Block(' detector configuration ', [
        BlockRow(
            Field(name='data acquisition system', dev='das_mesytec_fast_both', width=24),
            Field(name='tube pivot',   dev='tube_pivot_position', width=12),
            Field(name='tube height',  dev='tube', width=12),
            Field(name='table',        dev='table', width=12),
            Field(name='tube offset',  dev='tube_horizontal_offset', width=12, unit='mm'),
            Field(name='tube angle',   dev='tube_vertical_angle', width=12, unit='deg'),
            Field(name='total counts', dev='detector_count_rate', width=12),
            Field(name='count rate',   dev='detector_count_rate', width=12, unit='cps'),
            ),
        ],
    ),
)

# In _detarecol soll das aktuelle Bild des Detektors angezeigt
# und moeglichst alle 1 bis 2 Sekunde aktualisiert werden.
_detarecol = Column(
    Block(' active detector area ', [
        BlockRow(
            Field(dev='detector', picture='detector_area.png',
                width=68, height=50),
            ),
        ],
    ),
)

# In _histogramcol soll das Histogram aus der aktuell laufenden Messung
# berechnete und moeglichst alle 10 bis 30 Sekunden aktualisiert werden.
_histogramcol = Column(
    Block(' wavelength histogram ', [
        BlockRow(
            Field(dev='histogram', picture='histogram.png',
                width=50, height=50),
            ),
        ],
    ),
)

_beanstop1col = Column(
    Block('beamstop 1', [
        BlockRow(
            Field(name='status',   dev='stop1_on_off',  width=8),
            Field(name='hor pos',  dev='stop1_horizontal_position', width=8),
            Field(name='vert pos', dev='stop1_vertical_position', width=8),
            ),
        ],
    ),
)

_beanstop2col = Column(
    Block('beamstop 2', [
        BlockRow(
            Field(name='status',   dev='stop2_on_off',  width=8),
            Field(name='hor pos',  dev='stop2_horizontal_position', width=8),
            Field(name='vert pos', dev='stop2_vertical_position', width=8),
            ),
        ],
    ),
)

_momentumcol = Column(
    Block('momentum transfer', [
        BlockRow(
            Field(name='theta', dev='sample_theta',  width=8),
            Field(name='q_min', dev='q_min', width=8, unit='1/AA'),
            Field(name='q_max', dev='q_max', width=8, unit='1/AA'),
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
            Row(_detconfigcol),
            Row(_detarecol, _histogramcol),
            Row(_beanstop1col, _beanstop2col, _momentumcol),
        ],
    ),
)
