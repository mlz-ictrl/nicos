description = 'Optic Collimation and Slits [Monitor 12]'
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
                  options=['open', 'closed', 'safe'],
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
            Field(key='b1/mode', name='b\u2081',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok5a/mode', name='nok5a',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng', 'pola'],
                  width=6.5, height=wig_height),
            Field(key='zb0/mode', name='zb\u2080',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok5b/mode', name='nok5b',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='zb1/mode', name='zb\u2081',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok6/mode', name='nok6',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='zb2/mode', name='zb\u2082',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok7/mode', name='nok7',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='zb3/mode', name='zb\u2083',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok8/mode', name='nok8',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='bs1/mode', name='bs\u2081',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'point'],
                  width=6.5, height=wig_height),
            Field(key='nok9/mode', name='nok9',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['fc', 'vc', 'ng'],
                  width=6.5, height=wig_height),
            Field(key='b2/mode', name='b\u2082/h\u2082',
                  widget='nicos_mlz.refsans.gui.monitorwidgets.BeamPosition',
                  options=['slit', 'gisans', 'pinhole'],
                  width=6.5, height=wig_height),
            Field(key='b3/mode', name='b\u2083/h\u2083',
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

_ChopperBurg = Column(
    Block('Vertical Shifts for Optic Elements in the Chopper System', [
        BlockRow(
            Field(name='nok2\u1d63', dev='nok2.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok2\u209b', dev='nok2.sample', width=layout_width, unit='(mm)'),
            Field(name='nok3\u1d63', dev='nok3.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok3\u209b', dev='nok3.sample', width=layout_width, unit='(mm)'),
            Field(name='nok4\u1d63', dev='nok4.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok4\u209b', dev='nok4.sample', width=layout_width, unit='(mm)'),
            Field(name='disk3',      dev='disc3', width=layout_width, unit='(mm)'),
            Field(name='disk4',      dev='disc4', width=layout_width, unit='(mm)'),
            Field(name='b\u2081',    dev='b1.center', width=layout_width, unit='(mm)'),
        ),
        ],
    ),
)

_ChopperBurgQAD = Column(
    Block('Vertical Shifts for Optic Elements in the Chopper System QAD', [
        BlockRow(
            Field(name='nok2',      dev='nok2', width=2*layout_width, unit='(mm)'),
            Field(name='nok3',      dev='nok3', width=2*layout_width, unit='(mm)'),
            Field(name='nok4',      dev='nok4', width=2*layout_width, unit='(mm)'),
            Field(name='disk3',     dev='disc3', width=layout_width, unit='(mm)'),
            Field(name='disk4',     dev='disc4', width=layout_width, unit='(mm)'),
            Field(name='b\u2081',   dev='b1.center', width=layout_width, unit='(mm)'),
        ),
        ],
    ),
)


_SFKammer = Column(
    Block('Vertical Shifts for Optic Elements in the Neutron Guide System', [
        BlockRow(
            Field(name='nok5a\u1d63', dev='nok5a.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok5a\u209b', dev='nok5a.sample', width=layout_width, unit='(mm)'),
            Field(name='zb\u2080',    dev='zb0', width=layout_width, unit='(mm)'),
            Field(name='nok5b\u1d63', dev='nok5b.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok5b\u209b', dev='nok5b.sample', width=layout_width, unit='(mm)'),
            Field(name='zb\u2081',    dev='zb1', width=layout_width, unit='(mm)'),
            Field(name='nok6\u1d63',  dev='nok6.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok6\u209b',  dev='nok6.sample', width=layout_width, unit='(mm)'),
            Field(name='zb\u2082',    dev='zb2', width=layout_width, unit='(mm)'),
        ),
        BlockRow(
            Field(name='nok7\u1d63', dev='nok7.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok7\u209b', dev='nok7.sample', width=layout_width, unit='(mm)'),
            Field(name='zb\u2083',   dev='zb3.center', width=layout_width, unit='(mm)'),
            Field(name='nok8\u1d63', dev='nok8.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok8\u209b', dev='nok8.sample', width=layout_width, unit='(mm)'),
            Field(name='bs\u2081',   dev='bs1.center', width=layout_width, unit='(mm)'),
            Field(name='nok9\u1d63', dev='nok9.reactor', width=layout_width, unit='(mm)'),
            Field(name='nok9\u209b', dev='nok9.sample', width=layout_width, unit='(mm)'),
            Field(name='SC\u2082',   dev='sc2', width=layout_width, unit='(mm)'),
        ),
        ],
    ),
)
_SFKammerQAD = Column(
    Block('Vertical Shifts for Optic Elements in the Neutron Guide System QAD', [
        BlockRow(
            Field(name='nok5a',     dev='nok5a',        width=2*layout_width, unit='(mm)'),
            Field(name='zb\u2080',  dev='zb0',          width=layout_width, unit='(mm)'),
            Field(name='nok5b',     dev='nok5b',        width=2*layout_width, unit='(mm)'),
            Field(name='zb\u2081',  dev='zb1',          width=layout_width, unit='(mm)'),
            Field(name='nok6',      dev='nok6',         width=2*layout_width, unit='(mm)'),
            Field(name='zb\u2082',  dev='zb2',          width=layout_width, unit='(mm)'),
        ),
        BlockRow(
            Field(name='nok7',      dev='nok7',         width=2*layout_width, unit='(mm)'),
            Field(name='zb\u2083',  dev='zb3.center',   width=layout_width, unit='(mm)'),
            Field(name='nok8',      dev='nok8',         width=2*layout_width, unit='(mm)'),
            Field(name='bs\u2081',  dev='bs1.center',   width=layout_width, unit='(mm)'),
            Field(name='nok9',      dev='nok9',         width=2*layout_width, unit='(mm)'),
            Field(name='SC\u2082',  dev='sc2',          width=layout_width, unit='(mm)'),
        ),
        ],
    ),
)

_probort = Column(
    Block('Vertical/Horizontal Shifts for Optic Elements at Sample Position', [
        BlockRow(
            Field(name='b\u2082', dev='b2.center', width=layout_width, unit='(mm)'),
            Field(name='h\u2082', dev='h2_center', width=layout_width, unit='(mm)'),
            Field(name='b\u2083', dev='b3.center', width=layout_width, unit='(mm)'),
            Field(name='h\u2083', dev='h3.center', width=layout_width, unit='(mm)'),
        ),
        ],
    ),
)

_apertures_slits = Column(
    Block('Apertures for movable slits', [
        BlockRow(
            Field(name='b\u2081',  dev='b1.height', width=layout_width, unit='(mm)'),
            Field(name='zb\u2083', dev='zb3.height', width=layout_width, unit='(mm)'),
            Field(name='bs\u2081', dev='bs1.height', width=layout_width, unit='(mm)'),
            Field(name='b\u2082',  dev='b2.height', width=layout_width, unit='(mm)'),
            Field(name='h\u2082',  dev='h2_width', width=layout_width, unit='(mm)'),
            Field(name='b\u2083',  dev='b3.height', width=layout_width, unit='(mm)'),
            Field(name='h\u2083',  dev='h3.height', width=layout_width, unit='(mm)'),
        ),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_modecol),
            Row(_collimationcol),
            Row(_ChopperBurg),
            Row(_ChopperBurgQAD),
            Row(_SFKammerQAD),
            Row(_SFKammer),
            Row(_probort, _apertures_slits),
        ],
    ),
)
