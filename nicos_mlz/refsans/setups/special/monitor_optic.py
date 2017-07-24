# created by Martin Haese, Tel FRM 10763
# last modified 20.07.2017
# to call it
# ssh refsans@refsansctrl02 oder 01
# cd /refsanscontrol
# ./bin/nicos-monitor -S monitor_optic

description = 'REFSANS optic monitor'
group = 'special'

# Legende fuer _modecol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_modecol = Column(
    Block('Measurement configuration', [
        BlockRow(
            Field(name='mode', dev='gisans_reflectometry', width=14),
            Field(name='beam tilt', dev='zero_12_48mrad_free', width=14, unit='mrad'),
            Field(name='sample slit', dev='b2_b3', width=14),
            Field(name='collimation length', dev='b1-b2_b1-b3_zb3-b2_zb3-b3', width=14),
            Field(name='monitor', dev='1_2_3_none', width=14),
            Field(name='tube pivot', dev='1_to_13', width=14),
            Field(name='samp det dist', dev='sample_detector_distance', width=14, unit='mm'),
            Field(name='flight path', dev='chopper_to_detector', width=14, unit='mm'),
            ),
        ],
    ),
)

# Legende fuer _collimationcol
# comb = Kammblende, fuer punktkollimierten Strahl
# dump = beam dump for neutrons and gammas
# fc   = full collimated, Bereich ohne Spiegel
# in / out = in Benutzung oder nicht
# ng   = neuron guide, voll verspiegelter Bereich
# open / closed = geoeffnet oder nicht
# pola = polarisator
# rc   = radial collimator, fuer punktkollimierten Strahl
# slit = Schlitzblende, fuer schlitzverschmierten Strahl
# vc   = vertical collimated, seitlich verspiegelter Bereich
#
# widget='...' muss natuerlich fuer REFSANS gemacht werden

_collimationcol = Column(
    Block('beam guide setting',[
        BlockRow(
            Field(dev='shutter', name='shutter',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['open', 'closed'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['ng', 'dump'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok2',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['ng'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok3',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['ng','rc'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok4',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['ng','rc'],
                  width=6.5,height=9),
            Field(dev='slit', name='b1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok5a',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['fc','vc','ng','pola'],
                  width=6.5,height=9),
            Field(dev='slit', name='zb0',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok5b',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['fc','vc','ng'],
                  width=6.5,height=9),
            Field(dev='slit', name='zb1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok6',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['fc','vc','ng'],
                  width=6.5,height=9),
            Field(dev='slit', name='zb2',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok7',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['fc','vc','ng'],
                  width=6.5,height=9),
            Field(dev='slit', name='zb3',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok8',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['fc','vc','ng'],
                  width=6.5,height=9),
            Field(dev='slit', name='bs1',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='nok', name='nok9',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['fc','vc','ng'],
                  width=6.5,height=9),
            Field(dev='slit', name='b2',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['slit','comb'],
                  width=6.5,height=9),
            Field(dev='slit', name='b3',
                  widget='nicos.sans1.monitorwidgets.CollimatorTable',
                  options=['in','out'],
                  width=6.5,height=9),
            ),
        ],
    ),
)

# Legende fuer noks und Blenden
# begin = vertikale Position des reaktorseitigen Ende des Neutronenleiters
# end   = vertikale Position des probenseitigen Ende des Neutronenleiters
# angle = Winkel in mrad des Neutronenleiters, kann positiv oder negativ sein
# accuracy = Summe des Fehlerbetrages der einzelnen Antriebe

_nok1col = Column(
    Block('nok1', [
        BlockRow(Field(name='begin',    dev='nok1_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok1_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok1_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok1_accuracy', width=8)),
        ],
    ),
)

_nok2col = Column(
    Block('nok2', [
        BlockRow(Field(name='begin',    dev='nok2_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok2_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok2_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok2_accuracy', width=8)),
        ],
    ),
)

_nok3col = Column(
    Block('nok3', [
        BlockRow(Field(name='begin',    dev='nok3_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok3_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok3_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok3_accuracy', width=8)),
        ],
    ),
)

_nok4col = Column(
    Block('nok4', [
        BlockRow(Field(name='begin',    dev='nok4_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok4_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok4_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok4_accuracy', width=8)),
        ],
    ),
)

_sc1col = Column(
    Block('SC1', [  # slave chopper 1
        BlockRow(Field(name='disk 3', dev='chopper_disk3_zposition', width=8)),
        BlockRow(Field(name='disk 4', dev='chopper_disk4_zposition', width=8)),
        ],
    ),
)

_b1col = Column(
    Block('b1', [
        BlockRow(Field(name='position', dev='b1_position', width=8)),
        BlockRow(Field(name='opening',  dev='b1_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='b1_accuracy', width=8)),
        ],
    ),
)

_nok5acol = Column(
    Block('nok5a', [
        BlockRow(Field(name='begin',    dev='nok5a_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok5a_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok5a_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok5a_accuracy', width=8)),
        ],
    ),
)

_zb0col = Column(
    Block('zb0', [
        BlockRow(Field(name='position', dev='zb0_position', width=8)),
        BlockRow(Field(name='opening',  dev='zb0_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='zb0_accuracy', width=8)),
        ],
    ),
)

_nok5bcol = Column(
    Block('nok5b', [
        BlockRow(Field(name='begin',    dev='nok5b_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok5b_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok5b_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok5b_accuracy', width=8)),
        ],
    ),
)

_zb1col = Column(
    Block('zb1', [
        BlockRow(Field(name='position', dev='zb1_position', width=8)),
        BlockRow(Field(name='opening',  dev='zb1_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='zb1_accuracy', width=8)),
        ],
    ),
)

_nok6col = Column(
    Block('nok6', [
        BlockRow(Field(name='begin',    dev='nok6_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok6_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok6_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok6_accuracy', width=8)),
        ],
    ),
)

_zb2col = Column(
    Block('zb2', [
        BlockRow(Field(name='position', dev='zb2_position', width=8)),
        BlockRow(Field(name='opening',  dev='zb2_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='zb2_accuracy', width=8)),
        ],
    ),
)

_nok7col = Column(
    Block('nok7', [
        BlockRow(Field(name='begin',    dev='nok7_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok7_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok7_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok7_accuracy', width=8)),
        ],
    ),
)

_zb3col = Column(
    Block('zb3', [
        BlockRow(Field(name='position', dev='zb3_position', width=8)),
        BlockRow(Field(name='opening',  dev='zb3_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='zb3_accuracy', width=8)),
        ],
    ),
)

_nok8col = Column(
    Block('nok8', [
        BlockRow(Field(name='begin',    dev='nok8_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok8_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok8_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok8_accuracy', width=8)),
        ],
    ),
)

_bs1col = Column(
    Block('bs1', [
        BlockRow(Field(name='position', dev='bs1_position', width=8)),
        BlockRow(Field(name='opening',  dev='bs1_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='bs1_accuracy', width=8)),
        ],
    ),
)

_nok9col = Column(
    Block('nok9', [
        BlockRow(Field(name='begin',    dev='nok9_begin', width=8)),
        BlockRow(Field(name='end',      dev='nok9_end', width=8)),
        BlockRow(Field(name='angle',    dev='nok9_angle', width=8)),
        BlockRow(Field(name='accuracy', dev='nok9_accuracy', width=8)),
        ],
    ),
)

_sc2col = Column(
    Block('SC2', [  # slave chopper 2
        BlockRow(Field(name='disk 5', dev='chopper_disk5_zposition', width=8)),
        BlockRow(Field(name='disk 6', dev='chopper_disk6_zposition', width=8)),
        ],
    ),
)

_b2col = Column(
    Block('b2', [
        BlockRow(Field(name='position', dev='b2_position', width=8)),
        BlockRow(Field(name='opening',  dev='b2_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='b2_accuracy', width=8)),
        ],
    ),
)

_h2col = Column(
    Block('h2', [
        BlockRow(Field(name='position', dev='h2_position', width=8)),
        BlockRow(Field(name='opening',  dev='h2_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='h2_accuracy', width=8)),
        ],
    ),
)

_h3col = Column(
    Block('h3', [
        BlockRow(Field(name='position', dev='h3_position', width=8)),
        BlockRow(Field(name='opening',  dev='h3_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='h3_accuracy', width=8)),
        ],
    ),
)

_b3col = Column(
    Block('b3', [
        BlockRow(Field(name='position', dev='b3_position', width=8)),
        BlockRow(Field(name='opening',  dev='b3_opening', width=8)),
        BlockRow(Field(name='accuracy', dev='b3_accuracy', width=8)),
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
            Row(_modecol),
            Row(_collimationcol),
            Row(_nok1col, _nok2col, _nok3col, _nok4col, _sc1col, _b1col,
                _nok5acol, _zb0col, _nok5bcol, _zb1col, _nok6col),
            Row(_zb2col, _nok7col, _zb3col, _nok8col, _bs1col,
                _nok9col, _sc2col, _b2col, _h2col, _h3col, _b3col),
        ],
    ),
)
