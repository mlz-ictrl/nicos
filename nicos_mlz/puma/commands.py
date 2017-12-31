#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA specific command for the multi detector/analyzer setup."""

from nicos import session

from nicos.commands import helparglist, usercommand

from nicos.core.constants import BLOCK, FINAL, POINT, SCAN, SUBSCAN
from nicos.core.data.dataset import PointDataset, ScanDataset
from nicos.core.errors import NicosError
from nicos.core.params import Value
from nicos.core.scan import Scan, SkipPoint, StopScan

from nicos.utils import lazy_property

__all__ = (
    'multiadscan'
)


class ADPointDataset(PointDataset):

    settype = POINT
    countertype = POINT

    def __init__(self, **kwds):
        self.valuelist = kwds.pop('parameters', ())
        PointDataset.__init__(self, **kwds)

    @lazy_property
    def devvaluelist(self):
        ret = [self.canonical_values[v.name] for v in self.valuelist]
        return ret

    @lazy_property
    def devvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.devices), self.valuelist)

    @lazy_property
    def detvalueinfo(self):
        return (Value('timer', unit='s'), Value('monitor', unit='cts'),
                Value('ctr', unit='cts'))

    @lazy_property
    def detvaluelist(self):
        return self.results['det']


class ADScanDataset(ScanDataset):

    settype = SCAN
    countertype = SCAN

    def __init__(self, **kwds):
        self.valuelist = kwds.get('parameters', ())
        if self.valuelist:
            kwds.pop('parameters')
        ScanDataset.__init__(self, **kwds)

    @lazy_property
    def devvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.devices), self.valuelist)

    @lazy_property
    def detvalueinfo(self):
        return (Value('timer', unit='s', fmtstr='%.1f'),
                Value('monitor', unit='cts', fmtstr='%d'),
                Value('ctr', unit='cts', fmtstr='%d'))


class MultiADScan(Scan):

    def __init__(self, info_header, parnames, parlist, psipos, phipos, monopos,
                 cadpos, preset, detseq=1):
        detlist = [session.getDevice('det')]
        Scan.__init__(self, [], [], preset={'t': preset}, detlist=detlist,
                      scaninfo=info_header)
        cad = session.getDevice('cad')
        mono = session.getDevice('mono')
        phi = session.getDevice('phi')
        psi = session.getDevice('psi')
        self._ad_devices = [cad, mono, psi, phi]
        self._ad_positions = [cadpos, monopos, psipos, phipos]
        self._detseq = detseq
        self._parnames = [(v.split('/')[0:] or [''])[0] for v in parnames]
        self._parunits = [(v.split('/')[1:] or [''])[0] for v in parnames]
        self._paraValueinfo = tuple(Value(n, unit=u if u else 'rlu',
                                          fmtstr='%.2f') for n, u in
                                    zip(self._parnames, self._parunits))
        self._parlist = parlist
        # self._envlist[0:0] = self._ad_devices
        self._point = None
        self._data = session.data

    def prepareScan(self, positions):
        # XXX with actionscope
        session.beginActionScope('Moving to start')
        try:
            self.moveDevices(self._ad_devices, positions, wait=True)
        finally:
            session.endActionScope()

    def beginScan(self):
        # Copy of the data.manager.beginScan with s/ScanDataset/ADScanDataset/
        self._data._clean((BLOCK,))
        dataset = ADScanDataset(
            subscan=self._subscan,
            devices=self._devices,
            environment=self._envlist,
            detectors=self._detlist,
            preset=self._preset,
            info=self._scaninfo,
            npoints=self._npoints,
            xindex=self._xindex,
            startpositions=self._startpositions,
            endpositions=self._endpositions,
            continuation=self._continuation,
            cont_direction=self._cont_direction,
            parameters=self._paraValueinfo,
        )
        for sink in session.datasinks:
            if sink.isActive(dataset):
                handlers = sink.createHandlers(dataset)
                dataset.handlers.extend(handlers)
        if self._data._current:
            self._data._current.subsets.append(dataset)
            dataset.number = len(self._data._current.subsets)
        self._data._stack.append(dataset)
        # self.dataset = self._data._init(dataset)
        # XXX: when to clean these up?
        self.dataset = dataset
        self._data._last_scans.append(self.dataset)
        self.dataset.dispatch('prepare')
        self.dataset.dispatch('begin')
        session.elogEvent('scanbegin', self.dataset)

    def readPosition(self):
        actualpos = {}
        try:
            # remember the read values so that they can be used for the
            # data point
            if self._point is not None:
                session.log.info('readPosition: %r', actualpos)
                for i, dev in enumerate(self._parnames):
                    actualpos[dev] = (None, self._parlist[self._point][i])
        except NicosError as err:
            self.handleError('read', err)
        return actualpos

    def beginTemporaryPoint(self, **kwds):
        """Create and begin a point dataset that does not use datasinks."""
        self._data._clean((BLOCK, SCAN, SUBSCAN))
        self._data._updatePointKeywords(kwds)
        dataset = ADPointDataset(**kwds)
        return self._data._init(dataset, skip_handlers=True)

    def beginPoint(self, **kwds):
        """Create and begin a point dataset."""
        self._data._clean((BLOCK, SCAN, SUBSCAN))
        self._data._updatePointKeywords(kwds)
        dataset = ADPointDataset(**kwds)
        return self._data._init(dataset)

    def finishPoint(self):
        self._data.finishPoint()

    def finishTemporaryPoint(self):
        """Remove the current point dataset."""
        if self._data._current.settype != POINT:
            session.log.warning('no data point to finish here')
            return
        point = self._data._stack.pop()
        point.trimResult()
        self._data._current.subsets.pop()

    def _inner_run(self):
        try:
            self.prepareScan(self._ad_positions)
        except StopScan:
            return
        except SkipPoint:
            return

        det = self._detlist[0]
        detname = self._detlist[0].name
        try:
            self.preparePoint(0, [])
            self.beginScan()
            point = self.beginTemporaryPoint(target=self._ad_positions,
                                             detectors=self._detlist)
            self.acquire(point, self._preset)
            self.finishTemporaryPoint()
        finally:
            result = det.read()
            ct = result[0:2]  # timer, monitor
            if det._attached_images:  # setup with an image
                result = det.readArrays(FINAL)[0][0].astype('f').tolist()
            else:
                result = result[2:]
            if self._detseq == -1:
                result = list(reversed(result))
        try:
            for i, v in enumerate(result):
                self._point = i
                with self.pointScope(i + 1):
                    point = self.beginPoint(target=self._parlist[i],
                                            parameters=self._paraValueinfo)
                    if i == 0:
                        self._data.updateMetainfo()
                    values = {}
                    for n, pv in zip(self._parnames, self._parlist[i]):
                        values[n] = (None, pv)
                    self._data.putValues(values)
                    self._data.putResults(FINAL, {detname: (ct + [v], [])})
                    self.readEnvironment()
                    self.finishPoint()
        finally:
            self._point = None
            self.endScan()


@usercommand
@helparglist('')
def multiadscan(info_header, parnames, parlist, psipos, phipos, monopos,
                cadpos, preset, detseq=1):
    """Multi analyzer 'scan'.

    This is a single point scan. The detector data (monitor, timer, and the
    counters) will be rearranged as a 11 point scan.
    """
    MultiADScan(info_header, parnames, parlist, psipos, phipos, monopos,
                cadpos, preset, detseq).run()


# @usercommand
# @helparglist('')
# def MultiADscanOrig(info_header, parnames, parlist, psipos, phipos, monopos,
#                     cadpos, preset, detseq=1):

#     session.log.info('Multiscan: %r', cadpos)

#     cad = session.getDevice('cad')
#     det = session.getDevice('det')
#     mono = session.getDevice('mono')

#     inst = session.instrument
#     med = session.getDevice('med')
#     mfvpg = session.getDevice('mfvpg')
#     mfhpg = session.getDevice('mfhpg')
#     phi = session.getDevice('phi')
#     psi = session.getDevice('psi')
#     muslit_t = session.getDevice('muslit_t')

#     det_type = getattr(inst, 'detectortype', '3He multi')
#     session.log.info('inst.detectortype = %s', det_type)

#     error = 0
#     if det_type == 'PSD':
#         multiWait(med)
#     for i in range(5):
#         session.log.info('try #%d', i)
#         try:
#             if mono.status()[0] == status.OK:
#                 mono.move(monopos)
#             elif mono.status()[0] == status.ERROR:
#                 mono.reset()
#             if phi.status()[0] == status.OK:
#                 phi.move(phipos)
#             elif phi.status()[0] == status.ERROR:
#                 phi.reset()
#             if psi.status()[0] == status.OK:
#                 psi.move(psipos)
#             elif psi.status()[0] == status.ERROR:
#                 psi.reset()
#             if cad.status()[0] == status.OK:
#                 cad.move(cadpos)
#             elif cad.status()[0] == status.ERROR:
#                 cad.reset()
#             multiWait([phi, psi, cad, mono])
#         except PositionError:
#             session.log.warn('cad status %s', cad.status()[0])
#             session.log.warn('phi status %s', phi.status()[0])
#             session.log.warn('psi status %s', psi.status()[0])
#             session.log.warn('mono status %s', mono.status()[0])
#             session.log.warn('something is wrong')
#             if abs(psi.read() - psipos) > 0.1:
#                 error = 1
#                 msg = 'psi has not reached position'
#                 if psi.status()[0] == status.ERROR:
#                     psi.reset()
#             if abs(phi.read() - phipos) > 0.1:
#                 error = 1
#                 msg = 'phi has not reached position'
#                 if phi.status() == status.ERROR:
#                     phi.reset()
#             if abs(mono.read() - monopos) > 0.1:
#                 error = 1
#                 msg = 'mono has not reached position 0'
#                 if mono.status()[0] == status.ERROR:
#                     mono.reset()
#             #  vertical focusing
#             if mono.th.read() < 15.5:
#                 if abs(15.5 - mfvpg.read()) > mfvpg.precision:
#                     error = 1
#                     msg = 'mono has not reached position 1'
#                     if mfvpg.status() == status.ERROR:
#                         mfvpg.reset()
#             elif abs(mono.th.read() - mfvpg.read()) > mfvpg.precision:
#                 error = 1
#                 msg = 'mono has not reached position 2'
#                 if mfvpg.doStatus() == status.ERROR:
#                     mfvpg.reset()
#             #  horizontal focusing
#             if (mono.fmode == 'double'):
#                 if abs(mono.th.read() - mfhpg.read()) > mfhpg.precision:
#                     error = 1
#                     msg = 'mono has not reached position 3'
#                     if mfhpg.status()[0] == status.ERROR:
#                         mfhpg.reset()
#             if (mono.fmode == 'vertical'):
#                 if abs(4.0 - mfhpg.read()) > mfhpg.precision:
#                     error = 1
#                     msg = 'mono has not reached position 4'
#                     if mfhpg.status()[0] == status.ERROR:
#                         mfhpg.reset()
#             if abs(cad.read() - cadpos) > 0.1:
#                 error = 1
#                 msg = 'cad has not reached position'
#                 if cad.status()[0] == status.ERROR:
#                     cad.reset()
#         if error == 0:
#             break
#     if error == 1:
#         session.log.error(msg)
#         return

#     # det._preset(preset)

#     if det_type == 'PSD':
#         multiWait(muslit_t)
#         det._preset(preset)
#         result = count(preset)
#         textline = ' time = %r mon1 = %r' % (det.timer.read(), det.m1.read())
#         session.log.info(textline)
#         # DataBox._addtextline(textline)
#         textline = ''
#         hist = []
#         ist = 3
#         ifin = 960 + 3
#         for pname in parnames:
#             textline += '%10s ' % pname
#         session.log.info(textline)
#         # DataBox._addtextline(textline)
#         for j in range(11):
#             textline = ''
#             for i in range(len(parnames)):
#                 textline += '%10s ' % parlist[j][i]
#             session.log.info(textline)
#             # DataBox._addtextline(textline)
#         # DataBox._addtextline('PSD data')
#         for i in range(8):
#             hist.append(det.z1.detector.read()[ist:ifin])
#             ist += 960
#             ifin += 960
#         for i in range(960):
#             textline = '%d' % i
#             for j in range(7):
#                 textline += '%10s ' % hist[j][i]
#                 # textline +=  '  ' + repr(int(hist[j][i]))
#             session.log.debug(textline)
#             # DataBox._addtextline(textline)
#     else:
#         point = session.data.beginPoint(target=parlist[0])
#         for i in range(5):
#             # result = count(preset)
#             acquire(point, det)
#             result = det.read()
#             #  If MesyDaq send 0, count again
#             _sum = sum(result[-11:])
#             session.log.info('detector sum: %d', _sum)
#             if _sum != 0:
#                 break

#         textline = ' time = %r mon1 = %r' % (result[0], result[1])
#         session.log.info(textline)
#         # DataBox._addtextline(textline)
#         textline = ''
#         for pname in parnames:
#             textline += '%10s ' % pname
#         textline += '%10s ' % 'counts'
#         session.log.info(textline)
#         # DataBox._addtextline(textline)
#         for i in range(11):
#             try:
#                 # session.log.info('result len: %d', len(result))
#                 if detseq == 1:
#                     ct = result[0], result[i + 2]
#                 elif detseq == -1:
#                     ct = result[0], result[12 - i]
#                 point = session.data.beginPoint(target=parlist[i])
#                 read = {det.name: ct}
#                 session.log.info('%r %r', parlist[i], read)
#                 session.data.putResults(FINAL, read)
#                 # DataBox.addMultiPoint(parlist[i], ct)
#             finally:
#                 session.data.finishPoint()
