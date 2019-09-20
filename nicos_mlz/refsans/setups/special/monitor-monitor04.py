# coding: utf-8

description = 'Optic Collimation and Slits Monitor'
group = 'special'

layout_width = 10
layout_doubleslit = 25
layout_two = 15

# Legende fuer _modecol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_modecol = Column(
    Block('Optical configuration', [
        BlockRow(
            Field(name='Collimation', key='optic/mode', width=34),
            Field(name='Angle', dev='optic', width=34),
            ),
        ],
    ),
)

# Legend for _collimationcol
# comb = comb, for point-collimated beam
# dump = beam dump for neutrons and gammas
# fc = full collimated, area without mirror
# in / out = in use or not
# ng = neuron guide, fully mirrored area
# open / closed = open or not
# pola = polarizer
# rc = radial collimator, for point-collimated beam
# slit = slit diaphragm, for slit-smeared beam
# vc = vertical collimated, laterally mirrored area
#
# widget = '...' must of course be made for REFSANS

wig_height=5
_collimationcol = Column(
    Block('Beam Guide Settings',[
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
            Field(key='b2/mode', name='b2/h2',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'pinhole'],
                  width=6.5, height=wig_height),
            Field(key='b3/mode', name='b3/h3',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit'],#, 'gisans', 'pinhole'],
                  width=6.5, height=wig_height),
            ),
        ],
    ),
)

# Legend for noks and apertures
# begin = vertical position of the reactor-side end of the neutron guide
# end = vertical position of the sample end of the neutron guide
# angle = angle in mrad of the neutron guide, can be positive or negative
# accuracy = sum of the error amount of the individual drives

_shifts_NOK = Column(
    Block('Vertical shifts for optic elements', [
        BlockRow(Field(name=u'nok2\u1d63',  dev='nok2r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok3\u1d63',  dev='nok3r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok4\u1d63',  dev='nok4r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok5a\u1d63',  dev='nok5a_r', width=layout_width, unit='(mm)'),
                 Field(name=u'nok5b\u1d63',  dev='nok5b_r', width=layout_width, unit='(mm)'),
                 Field(name=u'nok6\u1d63',  dev='nok6r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok7\u1d63',  dev='nok7r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok8\u1d63',  dev='nok8r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok9\u1d63',  dev='nok9r_axis', width=layout_width, unit='(mm)'),
                 ),
        BlockRow(Field(name=u'nok2\u209b',  dev='nok2r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok3\u209b',  dev='nok3r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok4\u209b',  dev='nok4r_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok5a\u209b',  dev='nok5a_s', width=layout_width, unit='(mm)'),
                 Field(name=u'nok5b\u209b',  dev='nok5b_s', width=layout_width, unit='(mm)'),
                 Field(name=u'nok6\u209b',  dev='nok6s_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok7\u209b',  dev='nok7s_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok8\u209b',  dev='nok8s_axis', width=layout_width, unit='(mm)'),
                 Field(name=u'nok9\u209b',  dev='nok9s_axis', width=layout_width, unit='(mm)'),
                 ),
        ],
    ),
)

_shifts_single_elements = Column(
    Block('Vertical shifts for single elements', [
        BlockRow(
                 Field(name=u'SC\u2081',      dev='nok5b_r', width=layout_width, unit='(mm)'),
                 Field(name=u'zb\u2080',      dev='zb0', width=layout_width, unit='(mm)'),
                 Field(name=u'zb\u2081',      dev='zb1', width=layout_width, unit='(mm)'),
                 Field(name=u'zb\u2082',      dev='zb2', width=layout_width, unit='(mm)'),
                 Field(name=u'SC\u2082',      dev='sc2', width=layout_width, unit='(mm)'),
                 ),
        ],
    ),
)

_shifts_v_apertures_slits = Column(
    Block('Vertical positions and apertures for movable slits', [
        BlockRow(
                Field(name=u'b\u2081 center ',     dev='b1_center', width=layout_width, unit='(mm)'),
                Field(name=u'zb\u2083 center ',     dev='zb3_center', width=layout_width, unit='(mm)'),
                Field(name=u'bs\u2081 center ',     dev='bs1_center', width=layout_width, unit='(mm)'),
                Field(name=u'b\u2082 center ',     dev='b2_center', width=layout_width, unit='(mm)'),
                Field(name=u'b\u2083 center ',     dev='b3_center', width=layout_width, unit='(mm)'),
                ),
                BlockRow(
                Field(name=u'b\u2081 height',     dev='b1_open', width=layout_width, unit='(mm)'),
                Field(name=u'zb\u2083 height',     dev='zb3_open', width=layout_width, unit='(mm)'),
                Field(name=u'bs\u2081 height',     dev='bs1_open', width=layout_width, unit='(mm)'),
                Field(name=u'b\u2082 height',     dev='b2_open', width=layout_width, unit='(mm)'),
                Field(name=u'b\u2083 height',     dev='b3_open', width=layout_width, unit='(mm)'),
                ),
        ],
    ),
)

_shifts_h_apertures_slits = Column(
    Block('Horizontal positions and apertures for movable slits', [
        BlockRow(
                Field(name=u'h\u2082 center ',     dev='b2_center', width=layout_width, unit='(mm)'),
                Field(name=u'h\u2083 center ',     dev='b3_center', width=layout_width, unit='(mm)'),
                ),
                BlockRow(
                Field(name=u'h\u2082 width',     dev='h2_open', width=layout_width, unit='(mm)'),
                Field(name=u'h\u2083 width',     dev='h3_open', width=layout_width, unit='(mm)'),
                )
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
            Row(_shifts_NOK),
            Row(_shifts_single_elements, _shifts_v_apertures_slits, _shifts_h_apertures_slits),
        ],
    ),
)
