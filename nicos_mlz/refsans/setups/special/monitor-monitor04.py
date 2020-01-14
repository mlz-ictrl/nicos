# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last version by Gaetano Mangiapia, Tel 54839 on Jan 09th 2020

# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_chopper

description = 'Sample Environment and Miscellaneous [Monitor 04]'
group = 'special'

_tempcol = Column(
    Block('Julabo Thermostat Status', [
        BlockRow(
            Field(name='target temperature ', key='julabo_temp/target', width=10,  format = '%.2f', unit=u'(\u2103)'),
            Field(name='internal bath temperature ', dev='julabo_int', width=10,  format = '%.2f', unit=u'(\u2103)'),
            Field(name='external sensor temperature ', dev='julabo_ext', width=10,  format = '%.2f', unit=u'(\u2103)'),
            #Field(name='Cryostat', dev='temp_cryo', width=14, unit='(K)'),
            )
        ],
    setups = 'julabo',
    ),
)

_julabo_plot = Column(
    Block('Temperature history', [
        BlockRow(
            Field(widget='nicos.guisupport.plots.TrendPlot',
                width=60, height=30, plotwindow=1800,
                devices=['julabo_temp/target','julabo_ext', 'julabo_int'],
                names=['T set 30min','T int 30min', 'T ext 30 min'],
                legend=True,
                ),

            Field(widget='nicos.guisupport.plots.TrendPlot',
                width=60, height=30, plotwindow=12*3600,
                devices=['julabo_temp/target','julabo_ext', 'julabo_int'],
                names=['T set 12h','T int 12h', 'T ext 12h'],
                legend=True,
                ),
            ),
        ],
    setups = 'julabo',
    ),
)

_nima = Column(
    Block('Langmuir Trough Status', [
        BlockRow(
            Field(name='area surface', device='nima_area', width=10,  format = '%.1f', unit=u'(cm\u00b2)'),
            Field(name='pressure', device='nima_pressure', width=10,  format = '%.2f', unit='(mN/m)'),
            Field(name='barrier speed', device='nima_speed', width=10,  format = '%.2f', unit='(mm/s)'),
            )
        ],
    setups = 'nima',
    ),
)


_ubahn = Column(
    Block('U-Bahn', [
        BlockRow(
                 Field(name='Next train in', dev='Ubahn', istext=True, unit = '(min)'),
                ),
        ],
    ),
)

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
            Row(_tempcol ),
            Row(_julabo_plot),
            Row(_nima),
            #Row(_ubahn),
        ],
    ),
)
