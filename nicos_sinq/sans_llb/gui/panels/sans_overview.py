# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2026-present by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************
'''
A sketch display of a SANS beamline, displaying current status.
'''
from nicos.clients.gui.panels import Panel
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, WARN
from nicos.guisupport.qt import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPolygonItem, \
    QGraphicsItemGroup, QVBoxLayout, QGraphicsEllipseItem, QGraphicsRectItem, QBrush, \
    QColor, QGraphicsSimpleTextItem, Qt, QFont, QTimer, QGraphicsLineItem, QPen, QPolygonF, QPointF
from nicos.protocols.cache import cache_load, OP_TELL, cache_dump

STATUS_COLORS = {
    OK: QColor(0, 255, 0),
    WARN: QColor(255, 255, 0),
    BUSY: QColor(150, 150, 0),
    NOTREACHED: QColor(128, 0, 128),
    DISABLED: QColor(50, 50, 50),
    ERROR: QColor(255, 0, 0),
    UNKNOWN: QColor(128, 128, 128),
}

class InteractiveGroup(QGraphicsItemGroup):

    def __init__(self, groupname, *args, **opts):
        QGraphicsItemGroup.__init__(self, *args, **opts)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._name = groupname

    def mousePressEvent(self, event):
        self.scene().parent().childSelected(self._name)
        QGraphicsItemGroup.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.scene().parent().childActivated(self._name)
        QGraphicsItemGroup.mouseDoubleClickEvent(self, event)


class TransmittingGroup(QGraphicsItemGroup):

    def __init__(self, *args, **opts):
        QGraphicsItemGroup.__init__(self, *args, **opts)
        self._name = 'transmitter'

    def mousePressEvent(self, event):
        for child in self.childItems():
            if isinstance(child, InteractiveGroup) and child.isUnderMouse():
                return child.mousePressEvent(event)
        return QGraphicsItemGroup.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        for child in self.childItems():
            if isinstance(child, InteractiveGroup) and child.isUnderMouse():
                return child.mouseDoubleClickEvent(event)
        return QGraphicsItemGroup.mouseDoubleClickEvent(self, event)

class AttenuationMask(QGraphicsItemGroup):
    def __init__(self, R, brush):
        QGraphicsItemGroup.__init__(self)

        for row in range(7):
            posy = -200 + (row * 400)//6
            cols = 4 if (row%2)==0 else 3
            for col in range(cols):
                posx = -(200*cols)//4 + (col*(400*cols))//(4*(cols-1))
                hole = QGraphicsEllipseItem(-R+posx, -R+posy, 2*R, 2*R)
                hole.setBrush(brush)
                self.addToGroup(hole)

class SlitDisplay(InteractiveGroup):
    """
    Represents a 4-blade slit to be displayed in a frame overlaying other components.
    """
    size_factor = 200./60.

    def __init__(self, slit_name):
        self.slit_name = slit_name
        InteractiveGroup.__init__(self, "G_"+slit_name)
        self.build_frame()
        self.build_blades()
        self.move_blades(120, 120)
        self.set_status(DISABLED)

    def build_frame(self):
        txt = QGraphicsSimpleTextItem(self.slit_name)
        txt.setFont(QFont('sans', 200))
        txt.setPos(-txt.boundingRect().width()//2, 400)
        txt.setZValue(1)
        self.addToGroup(txt)

        background = QGraphicsRectItem(-600, -800, 1200, 1600)
        background.setBrush(QColor(255, 255, 255, 150))
        background.setPen(QPen(QColor(113,76,161), 100))
        background.setZValue(-5)
        self.addToGroup(background)

        size = int(self.size_factor*45.)
        beam = QGraphicsRectItem(-size//2, -size//2-100, size, size)
        beam.setBrush(QColor(0, 0, 0, 50))
        beam.setZValue(-1)
        self.addToGroup(beam)

    def build_blades(self):
        brush = QBrush(QColor(101,67,33, 255))

        left = QGraphicsRectItem(-300, -400, 300, 600)
        left.setBrush(brush)
        left.setZValue(-2)
        self.addToGroup(left)

        right = QGraphicsRectItem(0, -400, 300, 600)
        right.setBrush(brush)
        right.setZValue(-2)
        self.addToGroup(right)

        brush = QBrush(QColor(202,134,66, 255))

        top = QGraphicsRectItem(-300, -400, 600, 300)
        top.setBrush(brush)
        top.setZValue(-3)
        self.addToGroup(top)

        bottom = QGraphicsRectItem(-300, -100, 600, 300)
        bottom.setBrush(brush)
        bottom.setZValue(-3)
        self.addToGroup(bottom)

        self.blades = [left, right, top, bottom]

    def set_status(self, status):
        # sets the blade colors based on state but keeps top/bottom brighter
        left, right, top, bottom = self.blades
        left.setBrush(STATUS_COLORS[status].darker(200))
        right.setBrush(STATUS_COLORS[status].darker(200))
        top.setBrush(STATUS_COLORS[status])
        bottom.setBrush(STATUS_COLORS[status])


    def move_blades(self, xw, yh):
        left, right, top, bottom = self.blades
        xmove = int(xw/2.*self.size_factor)
        ymove = int(yh/2.*self.size_factor)
        left.setPos( -xmove, 0)
        right.setPos(xmove, 0)
        top.setPos(0, -ymove)
        bottom.setPos(0, ymove)

class SANSInstrumentSketch(Panel):
    _devinfo = {}

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self._view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-20_500, -3_000, 41_000, 6_500)
        self._view.setScene(self.scene)
        vbox.addWidget(self._view)

        self.guide_end = int(options.get('guide_end', (-20000)))
        self.polarizer = tuple(options.get('polarizer', ()))
        self.collimators = tuple(options.get('collimators', ()))
        self.samples = int(options.get('samples', 0))
        self.sample_changer = options.get('sample_changer', "unconfigured")

        self.build_background()
        self.build_samples()
        self.build_collimators()
        self.build_mask_changer()
        self.build_slits()
        self.build_detectors()

        self._currentSelection = None

        client.cache.connect(self.on_client_cache)
        client.connected.connect(self.on_client_connected)

        QTimer.singleShot(1000, self.resizeEvent)

    def build_background(self):
        s = self.scene

        guide = s.addRect(-20500, -200, 20500+self.guide_end, 400,
                          pen=QPen(QColor(0, 0, 0, 150), 100),
                          brush = QBrush(QColor(0, 0, 0, 50)))
        guide.setZValue(-11)

        if len(self.polarizer) == 3:
            _, _, end = self.polarizer
            vacuum = s.addRect(self.guide_end, -2500, end-self.guide_end, 5000,
                              pen=QPen(QColor(0, 0, 0, 100), 100))
            vacuum.setZValue(-11)
            col_start = end
            col_len = -1000-end
        else:
            col_start = self.guide_end
            col_len = -1000-self.guide_end
        vacuum = s.addRect(col_start, -1500, col_len, 3700,
                          pen=QPen(QColor(100, 0, 0, 100), 100),
                          brush = QBrush(QColor(100, 0, 0, 30)))
        vacuum.setZValue(-11)

        pen = QPen(QColor(0, 0, 0, 150), 30)
        self._vs_group = InteractiveGroup('G_vs')
        bg = QGraphicsRectItem(0, -400, 800, 800)
        bg.setBrush(QColor(50, 50, 50, 50))
        bg.setZValue(-10)
        self._vs_group.addToGroup(bg)
        for i in range(-3, 9):
            xi = max(i*150-400, 0)
            xo = min(i*150+400, 800)
            yi = -400 + max(0, (xi-i*150+400))
            yo = 400 - max(0, (i*150+400-xo))
            line = QGraphicsLineItem(xi, yi, xo, yo)
            line.setPen(pen)
            line.setZValue(-9)
            self._vs_group.addToGroup(line)
        self._vs_group.text=QGraphicsSimpleTextItem("Velocity\nSelector")
        self._vs_group.text.setFont(QFont('sans', 200))
        self._vs_group.text.setZValue(-8)
        self._vs_group.text.setPos(0, 400)
        self._vs_group.addToGroup(self._vs_group.text)
        self._vs_group.setZValue(-5)
        self._vs_group.setPos(-20300, 0)
        s.addItem(self._vs_group)

        detin = QPolygonF()
        detin.append(QPointF(160, 250))
        detin.append(QPointF(550, 2000))
        detin.append(QPointF(550, -2000))
        detin.append(QPointF(160, -250))
        s.addPolygon(detin, brush=QColor(150, 50, 50, 100)).setZValue(-11)

        dett = s.addRect(550, -2000, 19500, 4000)
        dett.setZValue(-11)
        dett.setBrush(QColor(150, 50, 50, 100))

        self._selectionText = QGraphicsSimpleTextItem('')
        self._selectionText.setFont(QFont('sans', 24))
        s.addItem(self._selectionText)
        self._selectionText.setPos(-150, 350)

    def update_samples(self):
        s = self.scene
        s.removeItem(self._samples_group)
        self._samples_group = None
        self.build_samples()

    def build_samples(self):
        s = self.scene

        self._samples_group = InteractiveGroup('G_samples')

        for sample_i in range(self.samples):
            smpl = s.addEllipse(-100, -100+250*sample_i, 200, 200)
            smpl.setBrush(QColor(50, 50, 150, 200))
            self._samples_group.addToGroup(smpl)

        txt = QGraphicsSimpleTextItem('1')
        txt.setFont(QFont('sans', 300))
        txt.setPos(-450, 150)
        txt.setZValue(-10)
        self._samples_group.addToGroup(txt)
        self._samples_group.txt = txt

        self._samples_group.setZValue(-11)
        self._samples_group.setPos(0,0)
        s.addItem(self._samples_group)


    def build_collimators(self):
        s = self.scene

        self._collimator_graphics={}
        pen = QPen(QColor(0, 0, 0, 150), 100)
        pen2 = QPen(QColor(0, 0, 0, 255), 100)
        brush = QBrush(QColor(0, 0, 0, 50))

        s.addLine(self.guide_end, 2500, self.guide_end, 3000, pen=pen2).setZValue(-10)
        txt = s.addSimpleText(f'{-self.guide_end/1000:.1f} m')
        txt.setPos(self.guide_end-300, 3100)
        txt.setFont(QFont('sans', 200))
        txt.setZValue(-10)

        if len(self.polarizer)==3:
            name, start, end = self.polarizer
            group = InteractiveGroup('G_'+name)
            guide = QGraphicsRectItem(start, -200, end-start, 400)
            guide.setPen(pen)
            guide.setBrush(brush)
            guide.setZValue(-9)
            group.addToGroup(guide)
            guide = QGraphicsRectItem(start, 800, end-start, 400)
            guide.setPen(pen)
            guide.setBrush(brush)
            guide.setZValue(-9)
            group.addToGroup(guide)

            length = end-start
            polmir = QGraphicsLineItem(start+length//10, 1000, start+length//2, 800)
            polmir.setPen(pen)
            guide.setZValue(-8)
            group.addToGroup(polmir)
            length = end-start
            polmir = QGraphicsLineItem(start+length*6//10, 1000, end, 800)
            polmir.setPen(pen)
            guide.setZValue(-8)
            group.addToGroup(polmir)
            length = end-start
            polmir = QGraphicsLineItem(start+length//10, 1000, start+length//2, 1200)
            polmir.setPen(pen)
            guide.setZValue(-8)
            group.addToGroup(polmir)
            length = end-start
            polmir = QGraphicsLineItem(start+length*6//10, 1000, end, 1200)
            polmir.setPen(pen)
            guide.setZValue(-8)
            group.addToGroup(polmir)

            ft = QGraphicsRectItem(start, -1300, end-start, 600)
            ft.setPen(pen)
            ft.setZValue(-9)
            group.addToGroup(ft)
            group.setPos(0, 1000)
            group.setZValue(-8)
            s.addItem(group)
            self._polarizer_graphics = group

            s.addLine(end, 2500, end, 3000, pen=pen2).setZValue(-10)
            txt = s.addSimpleText(f'{-end/1000:.1f} m')
            txt.setPos(end-300, 3100)
            txt.setFont(QFont('sans', 200))
            txt.setZValue(-10)

        for name, start, end in self.collimators:
            group = InteractiveGroup('G_'+name)
            guide = QGraphicsRectItem(start, -200, end-start, 400)
            guide.setPen(pen)
            guide.setBrush(brush)
            guide.setZValue(-5)
            group.addToGroup(guide)
            mask = QGraphicsLineItem((start+end)//2, 400, (start+end)//2, 800)
            mask.setPen(pen)
            mask.setZValue(-5)
            group.addToGroup(mask)
            mask = QGraphicsLineItem((start+end)//2, 1200, (start+end)//2, 1600)
            mask.setPen(pen)
            mask.setZValue(-5)
            group.addToGroup(mask)
            group.setPos(0, -1000)
            group.setZValue(-8)
            s.addItem(group)
            self._collimator_graphics[name] = group

            s.addLine(end, 2500, end, 3000, pen=pen2).setZValue(-10)
            txt = s.addSimpleText(f'{-end/1000:.1f} m')
            txt.setPos(end-300, 3100)
            txt.setFont(QFont('sans', 200))
            txt.setZValue(-10)

    def build_mask_changer(self):
        s = self.scene

        # pen = QPen(QColor(0, 0, 0, 150), 100)
        pen2 = QPen(QColor(0, 0, 0, 255), 100)
        brush = QBrush(QColor(101,67,33, 255))

        s.addLine(self.guide_end, -500, self.guide_end-200, -1500, pen=pen2).setZValue(-3)
        txt = s.addSimpleText('mask changer')
        txt.setPos(self.guide_end-800, -1900)
        txt.setFont(QFont('sans', 200))
        txt.setZValue(-2)

        background = s.addRect(self.guide_end-1400, -3200, 2000, 1700,
                          pen=pen2,
                          brush = QBrush(QColor(255, 255, 255, 150)))
        background.setZValue(-3)


        self._mask_changer=InteractiveGroup('G_mask_changer')
        self._mask_changer.text = txt

        cng = QPolygonF()
        cng.append(QPointF(-1000,-800))
        cng.append(QPointF(-1000,-200))
        cng.append(QPointF( -500, 300))
        cng.append(QPointF( 500,  300))
        cng.append(QPointF(1000, -200))
        cng.append(QPointF( 1000,-800))
        cngi = QGraphicsPolygonItem(cng)
        cngi.setPen(QPen(QColor(0, 0, 150, 255), 50))
        cngi.setBrush(QColor(200, 200, 200, 150))
        self._mask_changer.addToGroup(cngi)

        mask_frame = QGraphicsRectItem(-250, -250, 500, 500)
        mask_frame.setPen(QPen(QColor(0, 0, 50, 250), 30))
        mask_frame.setBrush(QColor(200, 255, 255, 255))
        mask_frame.setZValue(1)
        self._mask_changer.mask_fame = mask_frame
        self._mask_changer.addToGroup(mask_frame)

        # Pinhole default configuration
        # 0	open 43x43
        # 1	pinhole diam 30
        # 2	pinhole diam 20
        # 3	pinhole diam 10
        # 4	slit 10x42
        # 5	sieve 25 x pinhole diam 0.7
        # 6	sieve 25 x pinhole diam 0.24
        # 7	closed

        self._mask_changer.masks={}
        mask = QGraphicsRectItem(-215, -215, 430, 430)
        mask.setBrush(brush)
        mask.setZValue(2)
        self._mask_changer.masks["0"] = mask
        self._mask_changer.addToGroup(mask)

        for R, item_id in [(150, "1"), (100, "2"), (50, "3")]:
            mask = QGraphicsEllipseItem(-R, -R, 2*R, 2*R)
            mask.setBrush(brush)
            mask.setZValue(2)
            self._mask_changer.masks[item_id] = mask
            self._mask_changer.addToGroup(mask)
            mask.hide()

        mask = QGraphicsRectItem(-50, -210, 100, 420)
        mask.setBrush(brush)
        mask.setZValue(2)
        self._mask_changer.masks["4"] = mask
        self._mask_changer.addToGroup(mask)
        mask.hide()

        for R, mask_id in [(30, "5"), (10, "6")]:
            mask = AttenuationMask(R, brush)
            self._mask_changer.masks[mask_id] = mask
            self._mask_changer.addToGroup(mask)
            mask.setZValue(2)
            mask.hide()

        mask = QGraphicsEllipseItem(-2, -2, 5, 5)
        mask.setBrush(brush)
        mask.setZValue(2)
        self._mask_changer.masks["7"] = mask
        self._mask_changer.addToGroup(mask)
        mask.hide()

        self._mask_changer.setZValue(-1)
        self._mask_changer.setPos(self.guide_end-400, -2400)
        s.addItem(self._mask_changer)

    def build_slits(self):
        pen2 = QPen(QColor(113,76,161, 255), 100)

        self._slits = {}
        s = self.scene


        for slit, fr, to in [
            ('slit0', self.guide_end+50, self.guide_end+1500),
            ('slit1', -15500, -15500),
            ('slit4', -4200, -4200),
            ('slit5', -3000, -3000),
            ('slit6', -1090, -1090),
            ]:
            s.addLine(fr, -500, to, -1600, pen=pen2).setZValue(-3)

            self._slits[slit] = SlitDisplay(slit)
            self._slits[slit].setZValue(-1)
            self._slits[slit].setPos(to, -2400)
            s.addItem(self._slits[slit])

    def build_detectors(self):
        s = self.scene

        pen = QPen(QColor(0, 0, 0, 150), 75)
        pen2 = QPen(QColor(0, 0, 0, 255), 100)
        brush = QColor(0, 0, 0, 150)
        brush2 = QColor(0, 0, 0, 100)
        self._detector_graphics=InteractiveGroup('G_detector')

        rect = QGraphicsRectItem(0, -1500, 400, 3000)
        rect.setPen(pen)
        rect.setBrush(brush)
        self._detector_graphics.addToGroup(rect)
        line = QGraphicsLineItem(0, 2500, 0, 3000)
        line.setPen(pen2)
        self._detector_graphics.addToGroup(line)
        txt = s.addSimpleText(f'{3000/1000:.1f} m')
        txt.setPos(0, 3100)
        txt.setFont(QFont('sans', 200))
        self._detector_graphics.txt=txt
        self._detector_graphics.addToGroup(txt)

        self._detector_graphics.setPos(3000, 0)
        self._detector_graphics.setZValue(-2)
        s.addItem(self._detector_graphics)

        self._detector2_graphics=InteractiveGroup('G_detector2')

        rect = QGraphicsRectItem(0, -1500, 400, 3000)
        rect.setPen(pen)
        rect.setBrush(brush2)
        self._detector2_graphics.addToGroup(rect)
        rect = QGraphicsRectItem(0, -1500, 400, 1000)
        rect.setPen(pen)
        rect.setBrush(brush)
        self._detector2_graphics.addToGroup(rect)
        line = QGraphicsLineItem(0, 2500, 0, 3000)
        line.setPen(pen2)
        self._detector2_graphics.addToGroup(line)
        txt = s.addSimpleText(f'{1500/1000:.1f} m')
        txt.setPos(0, 3100)
        txt.setFont(QFont('sans', 200))
        self._detector2_graphics.txt=txt
        self._detector2_graphics.addToGroup(txt)

        self._detector2_graphics.setPos(1500, 0)
        self._detector2_graphics.setZValue(-2)
        s.addItem(self._detector2_graphics)


    def on_client_cache(self, data):
        (_, key, _, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.rsplit('/', 1)

        col_names = [ci[0] for ci in self.collimators]
        if ldevname in col_names:
            if subkey == 'status':
                value = cache_load(value)
                for item in self._collimator_graphics[ldevname].childItems():
                    if hasattr(item, 'setBrush'):
                        item.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                coll = self._collimator_graphics[ldevname]
                if value == 'ng':
                    coll.setPos(0, 0)
                elif value == 'ft':
                    coll.setPos(0, -1000)
                else:
                    # in transition?
                    coll.setPos(0, -500)
        if self.polarizer and ldevname == self.polarizer[0]:
            if subkey == 'status':
                value = cache_load(value)
                for item in self._polarizer_graphics.childItems():
                    if hasattr(item, 'setBrush'):
                        item.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                coll = self._polarizer_graphics
                if value == 'ng':
                    coll.setPos(0,  0)
                elif value == 'ft':
                    coll.setPos(0,  1000)
                elif value == 'pg':
                    coll.setPos(0, -1000)
                else:
                    # in transition?
                    coll.setPos(0, 500)
        if ldevname == 'velocity_selector':
            if subkey == 'status':
                value = cache_load(value)
                for item in self._vs_group.childItems():
                    if hasattr(item, 'setBrush') and not hasattr(item, 'setText'):
                        item.setBrush(STATUS_COLORS[value[0]])
        if ldevname=='wavelength':
            if subkey == 'value':
                value = cache_load(value)
                self._vs_group.text.setText(f"Velocity\nSelector\n{value:.3f} nm")
        if ldevname == 'att':
            if subkey == 'status':
                value = cache_load(value)
                for item in self._mask_changer.childItems():
                    if (hasattr(item, 'setBrush')  and item is not self._mask_changer.mask_fame
                           and item not in self._mask_changer.masks.values()):
                        item.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                for mask in self._mask_changer.masks.values():
                    mask.hide()
                mask = self._mask_changer.masks.get(value, self._mask_changer.masks["0"])
                mask.show()
                self._mask_changer.text.setText(f"Mask {value}")

        if ldevname == 'dtlz':
            if subkey == 'status':
                value = cache_load(value)
                for item in self._detector_graphics.childItems():
                    if hasattr(item, 'setBrush') and item is not self._detector_graphics.txt:
                        item.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                self._detector_graphics.setPos(value, self._detector_graphics.y())
                self._detector_graphics.txt.setText(f'{value/1000:.1f} m')
        if ldevname == 'dthz':
            if subkey == 'status':
                value = cache_load(value)
                for item in self._detector2_graphics.childItems():
                    if hasattr(item, 'setBrush') and item is not self._detector2_graphics.txt:
                        item.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                self._detector2_graphics.setPos(value, self._detector2_graphics.y())
                self._detector2_graphics.txt.setText(f'{value/1000:.1f} m')

        if ldevname == self.sample_changer:
            if subkey == 'status':
                value = cache_load(value)
                for item in self._samples_group.childItems():
                    if hasattr(item, 'setBrush') and item is not self._samples_group.txt:
                        item.setBrush(STATUS_COLORS[value[0]])
            if subkey == 'value':
                value = cache_load(value)
                self._samples_group.setPos(0, -250*(self.samples-value-1))
                self._samples_group.txt.setText(f'{value}')
                self._samples_group.txt.setPos(-650, -150+250*(self.samples-value-1))
            if subkey == 'mapping':
                # the sample holder type was change, could cause change in number of samples
                value = cache_load(value)
                self.samples = len(value)
                self.update_samples()

        if ldevname in self._slits:
            if subkey == 'status':
                value = cache_load(value)
                self._slits[ldevname].set_status(value[0])
            if subkey == 'value':
                value = cache_load(value)
                self._slits[ldevname].move_blades(*value)

    def on_client_connected(self):
        state = self.client.ask('getstatus')
        if not state:
            return
        devlist = ([ci[0] for ci in self.collimators]+
                   list(self._slits.keys())+['velocity_selector', 'att', self.sample_changer, 'dtlz', 'dthz'])
        if len(self.polarizer)>0:
            devlist.append(self.polarizer[0])

        for devname in devlist:
            self._create_device_item(devname)

    def _create_device_item(self, devname):
        ldevname = devname.lower()
        # get all cache keys pertaining to the device
        params = self.client.getDeviceParams(devname)
        if not params:
            return
        # let the cache handler process all properties
        for key, value in params.items():
            self.on_client_cache((1, ldevname + '/' + key, OP_TELL,
                                  cache_dump(value)))

    def resizeEvent(self, value=None):
        self._view.fitInView(self.scene.sceneRect(), mode=Qt.KeepAspectRatio)

    def childSelected(self, name):
        self._currentSelection = name
        self.on_client_connected()

    def childActivated(self, name):
        from nicos.clients.gui.panels.devices import DevicesPanel
        device_panel = self.window().findChildren(DevicesPanel)[0]
        if name in ['G_detector', 'G_detector2']:
            device_panel._open_control_dialog('detz')
        elif name.startswith('G_col'):
            device_panel._open_control_dialog('coll')
        elif name == 'G_vs':
            device_panel._open_control_dialog('wavelength')
        elif name == self.sample_changer:
            device_panel._open_control_dialog(self.sample_changer)
        elif name.startswith('G_slit'):
            device_panel._open_control_dialog(name[2:])
        elif name == 'G_mask_changer':
            device_panel._open_control_dialog('att')
