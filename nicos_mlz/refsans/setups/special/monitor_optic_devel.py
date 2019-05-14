# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last modified 01.02.2018
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_optic

description = 'optic collimation and slits'
group = 'special'

layout_width = 10
layout_doubleslit = 25
layout_two = 15

# Legende fuer _modecol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_modecol = Column(
    Block('Measurement configuration', [
        BlockRow(
            Field(name='Collimation', key='optic/mode', width=34),
            Field(name='Angle', dev='optic', width=34),
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
wig_hight=5
_collimationcol = Column(
    Block('beam guide setting',[
        BlockRow(
            Field(dev='shutter', name='shutter',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['open', 'closed'],
                  width=6.5, height=wig_hight),
            Field(dev='shutter_gamma', name='gamma',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['open', 'closed'],
                  width=6.5, height=wig_hight),
            Field(key='nok2/mode', name='nok2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['ng'],
                  width=6.5, height=wig_hight),
            Field(key='nok3/mode', name='nok3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['ng', 'rc'],
                  width=6.5, height=wig_hight),
            Field(key='nok4/mode', name='nok4',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['ng', 'rc'],
                  width=6.5, height=wig_hight),
            Field(key='b1/mode', name='b1',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_hight),
            Field(key='nok5a/mode', name='nok5a',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng', 'pola'],
                  width=6.5, height=wig_hight),
            Field(key='zb0/mode', name='zb0',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_hight),
            Field(key='nok5b/mode', name='nok5b',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_hight),
            Field(key='zb1/mode', name='zb1',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_hight),
            Field(key='nok6/mode', name='nok6',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_hight),
            Field(key='zb2/mode', name='zb2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_hight),
            Field(key='nok7/mode', name='nok7',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_hight),
            Field(key='zb3/mode', name='zb3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_hight),
            Field(key='nok8/mode', name='nok8',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_hight),
            Field(key='bs1/mode', name='bs1',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_hight),
            Field(key='nok9/mode', name='nok9',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_hight),
            Field(key='b2/mode', name='b2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'pinhole'],
                  width=6.5, height=wig_hight),
            Field(key='b3/mode', name='b3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'pinhole'],
                  width=6.5, height=wig_hight),
            ),
        ],
    ),
)

# Legende fuer noks und Blenden
# begin = vertikale Position des reaktorseitigen Ende des Neutronenleiters
# end   = vertikale Position des probenseitigen Ende des Neutronenleiters
# angle = Winkel in mrad des Neutronenleiters, kann positiv oder negativ sein
# accuracy = Summe des Fehlerbetrages der einzelnen Antriebe

_gammacol = Column(
    Block('gamma', [
        BlockRow(Field(name='position', dev='nok1_motor', width=layout_width)),
        ],
    ),
)

_nok2col = Column(
    Block('nok2', [
        BlockRow(Field(name='reactor',  dev='nok2r_axis', width=layout_width),
                 Field(name='sample',   dev='nok2s_axis', width=layout_width)),
        ],
    ),
)

_nok3col = Column(
    Block('nok3', [
        BlockRow(Field(name='reactor',  dev='nok3r_axis', width=layout_width),
                 Field(name='sample',   dev='nok3s_axis', width=layout_width)),
        ],
    ),
)

_nok4col = Column(
    Block('nok4', [
        BlockRow(Field(name='reactor',  dev='nok4r_axis', width=layout_width),
                 Field(name='sample',   dev='nok4s_axis', width=layout_width)),
        ],
    ),
)

_sc1col = Column(
    Block('SC1', [  # slave chopper 1
        BlockRow(Field(name='disk 3', dev='disc3', width=layout_width ),
                 Field(name='disk 4', dev='disc4', width=layout_width)),
        ],
    ),
)

_b1col = Column(
    Block('b1', [
        BlockRow(Field(name='position', dev='b1', width=layout_doubleslit)),
        ],
    ),
)

_nok5acol = Column(
    Block('nok5a', [
        BlockRow(Field(name='position', dev='nok5a', width=layout_two)),
        ],
    ),
)

_zb0col = Column(
    Block('zb0', [
        BlockRow(Field(name='position', dev='zb0', width=layout_width)),
        ],
    ),
)

_nok5bcol = Column(
    Block('nok5b', [
        BlockRow(Field(name='position', dev='nok5b', width=layout_two)),
        ],
    ),
)

_zb1col = Column(
    Block('zb1', [
        BlockRow(Field(name='position', dev='zb1', width=layout_width)),
        ],
    ),
)

_nok6col = Column(
    Block('nok6', [
        BlockRow(Field(name='pos',  dev='nok6', width=layout_two)),
        ],
    ),
)

_zb2col = Column(
    Block('zb2', [
        BlockRow(Field(name='position', dev='zb2', width=layout_width)),
        ],
    ),
)

_nok7col = Column(
    Block('nok7', [
        BlockRow(Field(name='reactor',  dev='nok7', width=layout_two)),
        ],
    ),
)

_zb3col = Column(
    Block('zb3', [
        BlockRow(Field(name='position', dev='zb3', width=layout_doubleslit)),
        ],
    ),
)

_nok8col = Column(
    Block('nok8', [
        BlockRow(Field(name='reactor',  dev='nok8', width=layout_two)),
        ],
    ),
)

_bs1col = Column(
    Block('bs1', [
        BlockRow(Field(name='position', dev='bs1', width=layout_doubleslit)),
        ],
    ),
)

_nok9col = Column(
    Block('nok9', [
        BlockRow(Field(name='reactor',  dev='nok9', width=layout_two)),
        ],
    ),
)

_sc2col = Column(
    Block('SC2', [  # slave chopper 2
        BlockRow(Field(name='sc2', dev='sc2', width=layout_width)),
        ],
    ),
)

_b2col = Column(
    Block('b2', [
        BlockRow(Field(name='pos',  dev='b2', width=layout_doubleslit)),
        ],
    ),
)

_h2col = Column(
    Block('h2', [
        BlockRow(Field(name='lateral', dev='h2_center', width=layout_width),
                 Field(name='width',  dev='h2_width', width=layout_width)),
        ],
    ),
)

_h3col = Column(
    Block('h3', [
        BlockRow( Field(name='position', dev='h3', width=layout_doubleslit),),
        ],
    ),
)

_b3col = Column(
    Block('b3', [
        BlockRow(Field(name='position', dev='b3', width=layout_doubleslit)),
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
            Row(_modecol),
            Row(_collimationcol),
            Row(_gammacol, _nok2col, _nok3col, _nok4col, _sc1col, _b1col),
            Row(_nok5acol, _zb0col, _nok5bcol, _zb1col, _nok6col, _zb2col,
                _nok7col, ),
            Row(_zb3col, _nok8col, _bs1col,
                _nok9col, _sc2col),
            Row(_b2col, _h2col, _h3col, _b3col),
        ],
    ),
)
