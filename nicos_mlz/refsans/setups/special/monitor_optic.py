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
wig_height=5
_collimationcol = Column(
    Block('beam guide setting',[
        BlockRow(
            Field(dev='shutter', name='shutter',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['open', 'closed'],
                  width=6.5, height=wig_height),
            Field(dev='shutter_gamma', name='gamma',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['open', 'closed'],
                  width=6.5, height=wig_height),
            Field(key='nok2/mode', name='nok2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['ng'],
                  width=6.5, height=wig_height),
            Field(key='nok3/mode', name='nok3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['ng', 'rc'],
                  width=6.5, height=wig_height),
            Field(key='nok4/mode', name='nok4',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['ng', 'rc'],
                  width=6.5, height=wig_height),
            Field(key='b1/mode', name='b1',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok5a/mode', name='nok5a',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng', 'pola'],
                  width=6.5, height=wig_height),
            Field(key='zb0/mode', name='zb0',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok5b/mode', name='nok5b',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='zb1/mode', name='zb1',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok6/mode', name='nok6',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='zb2/mode', name='zb2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok7/mode', name='nok7',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='zb3/mode', name='zb3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok8/mode', name='nok8',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='bs1/mode', name='bs1',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok9/mode', name='nok9',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='b2/mode', name='b2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'pinhole'],
                  width=6.5, height=wig_height),
            Field(key='b3/mode', name='b3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'pinhole'],
                  width=6.5, height=wig_height),
            ),
        ],
    ),
)

# Legende fuer noks und Blenden
# begin = vertikale Position des reaktorseitigen Ende des Neutronenleiters
# end   = vertikale Position des probenseitigen Ende des Neutronenleiters
# angle = Winkel in mrad des Neutronenleiters, kann positiv oder negativ sein
# accuracy = Summe des Fehlerbetrages der einzelnen Antriebe

_bending_cb_col = Column(
    Block('bending CB', [
        BlockRow(Field(name='nok2r',  dev='nok2r_axis', width=layout_width),
                 Field(name='nok2s',  dev='nok2s_axis', width=layout_width),
                 Field(name='nok3r',  dev='nok3r_axis', width=layout_width),
                 Field(name='nok3s',  dev='nok3s_axis', width=layout_width),
                 Field(name='nok4r',  dev='nok4r_axis', width=layout_width),
                 Field(name='nok4s',  dev='nok4s_axis', width=layout_width),
                 Field(name='disk 3', dev='disc3', width=layout_width ),
                 Field(name='disk 4', dev='disc4', width=layout_width),
                 Field(name='b1',     dev='b1.height', width=layout_width),
                 Field(name='nok5a_r',  dev='nok5a_r', width=layout_width),
                 Field(name='nok5a_s',  dev='nok5a_s', width=layout_width),
                 Field(name='zb0',      dev='zb0', width=layout_width),
                 ),
        ],
    ),
)

_bending_sfk_col = Column(
    Block('bending SFK', [  # slave chopper 1
        BlockRow(
                 Field(name='nok5b_r',  dev='nok5b_r', width=layout_width),
                 Field(name='nok5b_s',  dev='nok5b_s', width=layout_width),
                 Field(name='zb1',      dev='zb1', width=layout_width),
                 Field(name='nok6r',    dev='nok6r_axis', width=layout_width),
                 Field(name='nok6s',    dev='nok6s_axis', width=layout_width),
                 Field(name='zb2',      dev='zb2', width=layout_width),
                 Field(name='nok7r',    dev='nok7r_axis', width=layout_width),
                 Field(name='nok7s',    dev='nok7s_axis', width=layout_width),
                 Field(name='zb3 FAKE',      dev='zb2', width=layout_width),
                 Field(name='nok8r',    dev='nok8r_axis', width=layout_width),
                 Field(name='nok8s',    dev='nok8s_axis', width=layout_width),
                 Field(name='bs1 FAKE',      dev='zb2', width=layout_width),
                 ),
        ],
    ),
)
_bending_sfk2_col = Column(
    Block('bending SFK', [  # slave chopper 1
        BlockRow(
                 Field(name='nok9r',    dev='nok9r_axis', width=layout_width),
                 Field(name='nok9s',    dev='nok9s_axis', width=layout_width),
                 Field(name='sc2',      dev='sc2', width=layout_width),
                 Field(name='b2 FAKE',     dev='b1.height', width=layout_width),
                 Field(name='b3 FAKE',     dev='b1.height', width=layout_width),
                 ),
        ],
    ),
)

_slitcol = Column(
    Block('slits', [
        BlockRow(
                Field(name='b1',  dev='b1_open', width=layout_width),
                Field(name='zb3 FAKE',  dev='b1_open', width=layout_width),
                Field(name='bs1 FAKE',  dev='b1_open', width=layout_width),
                Field(name='b2 FAKE',  dev='b1_open', width=layout_width),
                Field(name='b3 FAKE',  dev='b1_open', width=layout_width),
                )
        ],
    ),
)

_aptcol = Column(
    Block('slits', [
        BlockRow(
                Field(name='primary_aperture',  key='primary_aperture/alias', width=layout_width),
                Field(name='value',  dev='primary_aperture', width=layout_width),
                Field(name='last_slit',  dev='last_slit', width=layout_width),
                Field(name='value FAKE',  dev='primary_aperture', width=layout_width),
                )
        ],
    ),
)

_widthcol = Column(
    Block('width', [
        BlockRow(
                Field(name='h2',  dev='h2_width', width=layout_width),
                Field(name='h3 FAKE',  dev='h2_width', width=layout_width),
                ),
        ],
    ),
)

_centercol = Column(
    Block('Y', [
        BlockRow(
                 Field(name='h2', dev='h2_center', width=layout_width),
                 Field(name='h3 FAKE', dev='h2_center', width=layout_width),
                 Field(name='gonio', dev='gonio_y', width=layout_width),
                 ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl01.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_modecol),
            Row(_collimationcol),
            Row(_bending_cb_col),
            Row(_bending_sfk_col),
            Row(_bending_sfk2_col, _centercol, _widthcol),
            Row(_slitcol, _aptcol),
        ],
    ),
)
