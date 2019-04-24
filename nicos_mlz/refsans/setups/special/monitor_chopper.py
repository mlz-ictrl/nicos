# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last modified 01.02.2018
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_chopper

description = 'chopper monitor'
group = 'special'

# Legende fuer _chconfigcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_chconfigcol = Column(
    Block(' chopper configuration ', [
        BlockRow(
            Field(name='Lambda Min', key='chopper/wlmin', width=14, unit='AA'),
            Field(name='Lambda Max', key='chopper/wlmax', width=14, unit='AA'),
            Field(name='disc2 [1-6]', dev='chopper_resolution', width=14),
            Field(name='maximum flight path', key='chopper/dist', width=14, unit='Meter'),
            Field(name='real flight path', dev='real_flight_path', width=14, unit='Meter'),
            # Field(name='real flight path', dev='real_flight_path', width=14, unit='m'),
            Field(name='wavelength res.', dev='resolution', width=14, unit='%'),
            ),
        ],
    ),
    Block(' real chopper setting ', [
         BlockRow(
            Field(name='speed', dev='chopper1', width=10),
            Field(name='gap', key='chopper/gap', width=10),
            Field(name='Modus', key='chopper/mode', width=24),
            Field(name='real', key='chopper2/pos', width=10),
            Field(name='START delay', key='chopper/delay', unit='deg', width=24),
            Field(name='Fatal', key='chopper/fatal', width=10),
            ),
        ],
    ),
)

# Das Time-Distance Diagramm wird von chopperconfig als png-Bild erzeugt
# und soll dann angezeigt werden. Breite und Hohe muss angepasst werden.

_tididiagcol = Column(
    Block(' time distance diagram ONLY SYMBOL!', [
        BlockRow(
            Field(widget='nicos_mlz.refsans.gui.monitorwidgets.TimeDistance',
                  width=57, height=48),
            ),
        ],
    ),
)

# Legende fuer die Chopperscheiben
# speed  = Umdrehungen pro Minute
# angle  = Winkel
# phase  = Phase
# gear   = Drehzahl-Faktor
# status = Fehlerstatus

_disk1col = Column(
    Block('disk 1', [
        BlockRow(Field(name='speed',  dev='chopper1',  width=6.5, unit='rpm')),
        ],
    ),
)

_disk2col = Column(
    Block('disk 2', [
        BlockRow(Field(name='phase',  key='chopper2/phase',  width=6.5, unit='deg')),
        ],
    ),
)

_disk3col = Column(
    Block('disk 3', [
        BlockRow(Field(name='phase',  key='chopper3/phase',  width=6.5, unit='deg')),
        ],
    ),
)

_disk4col = Column(
    Block('disk 4', [
        BlockRow(Field(name='phase',  key='chopper4/phase',  width=6.5, unit='deg')),
        ],
    ),
)

_disk5col = Column(
    Block('disk 5', [
        BlockRow(Field(name='phase',  key='chopper5/phase',  width=6.5, unit='deg')),
        ],
    ),
)

_disk6col = Column(
    Block('disk 6', [
        BlockRow(Field(name='phase',  key='chopper6/phase',  width=6.5, unit='deg')),
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
            Row(_chconfigcol),
            Row(_tididiagcol),
            Row(_disk2col, _disk3col, _disk4col,
                _disk5col, _disk6col),
        ],
    ),
)
