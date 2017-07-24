# created by Martin Haese, Tel FRM 10763
# last modified 21.07.2017
# to call it
# ssh refsans@refsansctrl02 oder 01
# cd /refsanscontrol
# ./bin/nicos-monitor -S monitor_chopper

description = 'REFSANS chopper monitor'
group = 'special'

# Legende fuer _chconfigcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_chconfigcol = Column(
    Block(' chopper configuration ', [
        BlockRow(
            Field(name='lambda min', dev='chopper_lambda_min', width=14, unit='AA'),
            Field(name='lambda max', dev='chopper_lambda_max', width=14, unit='AA'),
            Field(name='resolution', dev='chopper_delta_lambda_lambda', width=14),
            Field(name='flight path', dev='chopper_to_detector', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _diskcol
# run      = Scheibe rotiert
# stop     = Scheibe steht im Strahl mit Drehzahl Null
# gap 1..6 = Luecken zwischen den Neutronenleitern Nummer 1 bis 6
# empty    = Die Luecke ist ohne Scheibe
# disk 2   = Scheibe 2 ist in dieser Luecke
# out      = Diese Scheibe ist nicht im Strahl
#
# widget='...' muss natuerlich fuer REFSANS gemacht werden

_diskcol = Column(
    Block('chopper disk setting',[
        BlockRow(
            Field(dev='ch_disk1', name='disk 1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['run', 'stop'],
                  width=8, height=18),
            Field(dev='ch_disk2', name='disk 2',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['virt 6', 'gap 5', 'gap 4', 'gap 3',
                            'gap 2', 'gap 1', 'stop', 'out'],
                  width=8, height=18),
            Field(dev='ch_disk3', name='disk 3',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['gap 6', 'gap 5', 'stop', 'out'],
                  width=8, height=18),
            Field(dev='ch_disk4', name='disk 4',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['gap 6', 'gap 5', 'stop', 'out'],
                  width=8, height=18),
            Field(dev='ch_disk5', name='disk 5',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['run', 'stop'],
                  width=8, height=18),
            Field(dev='ch_disk6', name='disk 6',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['run', 'stop'],
                  width=8, height=18),
            ),
        ],
    ),
)

# Das Time-Distance Diagramm wird von chopperconfig als png-Bild erzeugt
# und soll dann angezeigt werden. Breite und Hohe muss angepasst werden.

_tididiagcol = Column(
    Block(' time distance diagram ', [
        BlockRow(
            Field(dev='td_diag', picture='time_distance.png',
                width=64, height=48),
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
        BlockRow(Field(name='angle',  dev='disk1_angle',  width=6.5)),
        BlockRow(Field(name='gear',   dev='disk1_gear',   width=6.5)),
        BlockRow(Field(name='status', dev='disk1_status', width=6.5)),
        ],
    ),
)

_disk2col = Column(
    Block('disk 2', [
        BlockRow(Field(name='phase',  dev='disk2_phase',  width=6.5)),
        BlockRow(Field(name='gear',   dev='disk2_gear',   width=6.5)),
        BlockRow(Field(name='status', dev='disk2_status', width=6.5)),
        ],
    ),
)

_disk3col = Column(
    Block('disk 3', [
        BlockRow(Field(name='phase',  dev='disk3_phase',  width=6.5)),
        BlockRow(Field(name='gear',   dev='disk3_gear',   width=6.5)),
        BlockRow(Field(name='status', dev='disk3_status', width=6.5)),
        ],
    ),
)

_disk4col = Column(
    Block('disk 4', [
        BlockRow(Field(name='phase',  dev='disk4_phase',  width=6.5)),
        BlockRow(Field(name='gear',   dev='disk4_gear',   width=6.5)),
        BlockRow(Field(name='status', dev='disk4_status', width=6.5)),
        ],
    ),
)

_disk5col = Column(
    Block('disk 5', [
        BlockRow(Field(name='phase',  dev='disk5_phase',  width=6.5)),
        BlockRow(Field(name='gear',   dev='disk5_gear',   width=6.5)),
        BlockRow(Field(name='status', dev='disk5_status', width=6.5)),
        ],
    ),
)

_disk6col = Column(
    Block('disk 6', [
        BlockRow(Field(name='phase',  dev='disk6_phase',  width=6.5)),
        BlockRow(Field(name='gear',   dev='disk6_gear',   width=6.5)),
        BlockRow(Field(name='status', dev='disk6_status', width=6.5)),
        ],
    ),
)

_mccol = Column(
    Block('MC', [   # disk 1 and 2
        BlockRow(Field(name='speed',      dev='disk1_speed',  width=6.5)),
        BlockRow(Field(name='disk2 pos',  dev='disk2_pos',  width=6.5)),
        BlockRow(Field(name='dist d2-d1', dev='distance_disk2_disk1', width=6.5)),
        ],
    ),
)

_sc1col = Column(
    Block('SC1', [   # disk 3 and 4
        BlockRow(Field(name='speed',   dev='SC1_speed',  width=6.5)),
        BlockRow(Field(name='phase',   dev='SC1_phase', width=6.5)),
        BlockRow(Field(name='opening', dev='SC1_opening_angle', width=6.5)),
        ],
    ),
)

_sc2col = Column(
    Block('SC2', [   # disk 5 and 6
        BlockRow(Field(name='speed',   dev='SC2_speed',  width=6.5)),
        BlockRow(Field(name='phase',   dev='SC2_phase', width=6.5)),
        BlockRow(Field(name='opening', dev='SC2_opening_angle', width=6.5)),
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
            Row(_chconfigcol),
            Row(_diskcol, _tididiagcol),
            Row(_disk1col, _disk2col, _disk3col, _disk4col,
                _disk5col, _disk6col, _mccol, _sc1col, _sc2col),
        ],
    ),
)
