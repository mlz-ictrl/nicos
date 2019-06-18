from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import usercommand
from nicos.commands.analyze import _getData, fit
from nicos.core import Attach, Measurable, Param, SubscanMeasurable, Value, \
    anytype, listof
from nicos.core.scan import Scan
from nicos.utils.fitting import CosineFit


@usercommand
def amplscan(dev1, start1, step1, numpoints1,
             dev2, start2, step2, numpoints2,
             t):
    scandet = session.getDevice('scandet')
    scandet.scandev = str(dev2)
    scandet.positions = [start2 + i*step2 for i in range(numpoints2)]
    dev1pos = [[start1 + i*step1] for i in range(numpoints1)]
    ds = Scan([session.getDevice(dev1)], dev1pos, None, detlist=[scandet],
              preset={'t': t}).run()
    fit(CosineFit, 'A', dataset=ds)


class ScanningDetector(SubscanMeasurable):
    """Generic "super" detector that scans over a configured device and counts
    with a given detector."""

    attached_devices = {
        'detector': Attach('Detector to scan', Measurable),
    }

    parameters = {
        'scandev':    Param('Current device to scan', type=str, settable=True),
        'positions':  Param('Positions to scan over', type=listof(anytype),
                            settable=True),
        'readresult': Param('Storage for processed results from detector, to'
                            'be returned from doRead()', type=listof(anytype),
                            settable=True, internal=True),
    }

    fitcls = CosineFit

    def doInit(self, mode):
        self._preset = None
        self._nparams = len(self.fitcls.fit_params)

    def doSetPreset(self, **preset):
        self._preset = preset

    def doStart(self):
        positions = [[p] for p in self.positions]
        ds = Scan(
            [session.getDevice(self.scandev)],
            positions, None, detlist=[self._attached_detector],
            preset=self._preset, subscan=True
        ).run()
        xs, ys, dys, _, ds = _getData()
        fit = self.fitcls()
        res = fit.run(xs, ys, dys)
        if res._failed:
            self.log.warning('Fit failed: %s.' % res._message)
            self.readresult = [0] * (self._nparams * 2)
        else:
            session.notifyFitCurve(ds, fit.fit_title, res.curve_x, res.curve_y)
            readres = []
            for par, err in zip(res._pars[1], res._pars[2]):
                readres.append(par)
                readres.append(err)
            self.readresult = readres

    def valueInfo(self):
        res = []
        for p in self.fitcls.fit_params:
            res.append(Value(p, type='other', errors='next'))
            res.append(Value('d' + p, type='error'))
        return tuple(res)

    def doRead(self, maxage=0):
        return self.readresult

    def doFinish(self):
        pass
