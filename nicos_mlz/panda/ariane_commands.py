#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Implementation of the ARIANE based scan optimizations.

See https://jugit.fz-juelich.de/ainx/ariane

Requires a running ARIANE server, whose location is configured as the
`ariane_host` parameter of the experiment device.
"""

import json
from time import time as currenttime

import numpy as np
import zmq

from nicos import session
from nicos.commands import usercommand
from nicos.commands.scan import _handleScanArgs, _infostr
from nicos.commands.tas import _getQ
from nicos.core import CommunicationError, NicosError, UsageError, SIMULATION
from nicos.core.scan import QScan
from nicos.utils.messaging import nicos_zmq_ctx

from nicos_mlz.panda.gui.ariane_vis import make_map, update_map


__all__ = ['qaigrid', 'qaiscan']


@usercommand
def qaigrid(Q0, Q1, Q2, *args, **kwargs):
    """Make a grid within a Q/E plane, usable as the initial points for a
    `qaiscan()`.

    You need to provide a rectangle of Q space to measure in, given by three
    Q vectors to lower-left, lower-right and upper-left corners.  For example,

    >>> qaiscan([1, 0, 0, 0], [2, 0, 0, 0], [1, 0, 0, 5], ...)

    would scan in this reactangle::

       [1, 0, 0, 5] +--------+ [2, 0, 0, 5]
                    |        |
                    |        |
       [1, 0, 0, 0] +--------+ [2, 0, 0, 0]

    Special keyword arguments:

    * initpoints: specify the size of initial grid to measure, can also
      be [n1, n2] for different size along the axes

    Other arguments are interpreted as for a normal `qscan`.
    """
    kwargs['initonly'] = True
    qaiscan(Q0, Q1, Q2, *args, **kwargs)


@usercommand
def qaiscan(Q0, Q1, Q2, *args, **kwargs):
    """Scan within a Q/E plane, letting the ARIANE algorithm select the
    precise scan locations.

    You need to provide a rectangle of Q space to measure in, given by three
    Q vectors to lower-left, lower-right and upper-left corners.  For example,

    >>> qaiscan([1, 0, 0, 0], [2, 0, 0, 0], [1, 0, 0, 5], ...)

    would scan in this reactangle::

       [1, 0, 0, 5] +--------+ [2, 0, 0, 5]
                    |        |
                    |        |
       [1, 0, 0, 0] +--------+ [2, 0, 0, 0]

    Special keyword arguments:

    * initpoints: specify the size of initial grid to measure, can also
      be [n1, n2] for different size along the axes
    * initscans: specify a scan number or list of scan numbers to use as the
      initial points, instead of measuring them again
    * maxpoints: specify the maximum total number of points to measure
    * maxtime: specify the maximum total time for the scan to take,
      including instrument moves, in seconds
    * background: specify a threshold in detector counts, below which
      counts are considered as background and removed for consideration by
      the algorithm.
    * intensity_threshold: specify a threshold in detector counts,
      above which exact counts are not used by the AI algorithm
      to determine the next point.

    Other arguments are interpreted as for a normal `qscan`.
    """
    # TODO: allow selecting counter/monitor columns

    maxpts = kwargs.pop('maxpoints', None)
    maxtime = kwargs.pop('maxtime', None)
    initpts = kwargs.pop('initpoints', 11)
    initscans = kwargs.pop('initscans', None)
    initres = kwargs.pop('initres', None)
    initonly = kwargs.pop('initonly', False)
    int_threshold = kwargs.pop('intensity_threshold', None)
    background = kwargs.pop('background', None)
    if not isinstance(initpts, (list, tuple)):
        initpts = [int(initpts), int(initpts)]

    q0 = np.array(_getQ(Q0, 'Q0')).astype(float)
    q1 = np.array(_getQ(Q1, 'Q1')).astype(float)
    q2 = np.array(_getQ(Q2, 'Q2')).astype(float)

    scanstr = _infostr('qaigrid' if initonly else 'qaiscan',
                      (Q0, Q1, Q2) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)
    if multistep:
        raise UsageError('Multi-step scan points are impossible with ARIANE')
    scan = QAIScan(q0, q1, q2, initpts=initpts, initscans=initscans, initres=initres,
                   initonly=initonly, maxpts=maxpts, maxtime=maxtime,
                   background=background, int_threshold=int_threshold,
                   firstmoves=move, detlist=detlist, envlist=envlist,
                   preset=preset, scaninfo=scaninfo)
    qaiscan.last = scan  # for debugging purposes
    scan.run()


class QAIScan(QScan):
    """Specialized Scan class for ARIANE scans."""
    ID = b'ARIANE'
    _socket = None

    # pylint: disable=too-many-arguments
    def __init__(self, q0, q1, q2, initpts, initscans, initres, initonly, maxpts,
                 maxtime, background, int_threshold, firstmoves=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None):

        # first establish connection
        hostport = getattr(session.experiment, 'ariane_host', None)
        if not hostport:
            raise UsageError('Cannot perform scan: ARIANE not configured')
        if session.mode != SIMULATION:
            self._connect(hostport)
            # ensure service is up and running
            version = self._request('ping')['version']
            session.log.debug('connected to ARIANE version %s', version)

        # conversion between Q/E and AI coordinates

        # apply heuristics to make q0 and the directions as simple as possible
        # by adjusting the limits
        offset, dir1, lim1, dir2, lim2 = determine_axes(q0, q1, q2)

        # see _pos2loc and _loc2pos for the conversions using these matrices
        self._q0 = offset
        self._qw = np.concatenate((dir1.reshape((4, 1)),
                                   dir2.reshape((4, 1))), axis=1)
        self._invqw = np.linalg.inv(self._qw.T @ self._qw) @ self._qw.T
        self._lim = [lim1, lim2]
        self._dlim = dlim = [lim1[1] - lim1[0], lim2[1] - lim2[0]]

        self._initonly = initonly
        self._maxpts = maxpts
        self._maxtime = maxtime
        self._background = background
        self._int_threshold = int_threshold
        self._last_loc = None
        self._travel_cost_sim = None

        # initial grid positions to measure
        self._initial_pos = []
        # initial results from other scans
        self._initial_res = []

        # handle travel cost grid

        n_grid = 31
        # the grid in terms of AI locations
        self._locgrid = [[lim1[0] + i * dlim[0] / (n_grid - 1),
                          lim2[0] + j * dlim[1] / (n_grid - 1)]
                         for i in range(n_grid) for j in range(n_grid)]
        # the grid in terms of Q positions
        self._posgrid = [self._loc2pos(loc) for loc in self._locgrid]

        # handle initialization points

        grid_locs = []
        ni1, ni2 = [x | 1 for x in initpts]  # must be odd
        total_initpts = (initpts[0] * initpts[1]) // 2

        if maxpts and maxpts < total_initpts:
            raise UsageError('Maximum number of points is too small; it '
                             'includes the %d initial points' %
                             total_initpts)

        # make a grid like this:  * * * *
        # (going in alternate      * * *
        # directions)             * * * *
        for j in range(0, ni2):
            irange = range(0, ni1) if j % 2 == 0 else range(ni1-1, -1, -1)
            for i in irange:
                if i % 2 != j % 2:
                    continue
                grid_locs.append([lim1[0] + i * dlim[0] / (ni1 - 1),
                                  lim2[0] + j * dlim[1] / (ni2 - 1)])
        grid_locs = np.array(grid_locs)

        if initscans:
            # add points from existing scans, remove points from the grid

            if initonly:
                raise UsageError('"initscans" makes no sense with "initonly"')

            # take from other scans?
            if isinstance(initscans, int):
                initscans = [initscans]

            session.log.info('Processing initial points from scans...')
            initscans = set(initscans)
            init_locs = []

            last_datasets = session.experiment.data.getLastScans()
            sel_datasets = []

            for (i, dataset) in enumerate(reversed(last_datasets), start=1):
                if -i in initscans:  # allow "-1" to refer to the last scan
                    initscans.discard(-i)
                    sel_datasets.append(dataset)
                if dataset.counter in initscans:
                    initscans.discard(dataset.counter)
                    sel_datasets.append(dataset)

            for dataset in sel_datasets:
                for subset in dataset.subsets:
                    try:
                        if self._isInScanArea(subset):
                            result = self._extractResult(subset)
                            self._initial_res.append(result)
                            init_locs.extend(result[0])
                    except Exception:
                        session.log.warning('Scan %d: could not extract '
                                            'results for AI from point %d',
                                            dataset.counter, subset.number,
                                            exc=1)

            session.log.info('%d valid point(s) extracted', len(init_locs))

            if initscans:
                session.log.warning('No dataset found for scan(s) %s',
                                    ', '.join(map(str, initscans)))

            if not self._initial_res:
                raise NicosError('No results found to populate the '
                                 'initial point grid')

            dx1 = (dlim[0] / (ni1 - 1) * 0.99) ** 2
            dx2 = (dlim[1] / (ni2 - 1) * 0.99) ** 2

            init_locs = np.array(init_locs)
            is_not_covered = np.all(np.sum(
                (grid_locs[:, np.newaxis, :] - init_locs)**2 / [dx1, dx2],
                axis=2) > 1, axis=1)
            grid_locs = grid_locs[is_not_covered]

        if initres:
            for res in initres:
                locs = [self._pos2loc(res[:4])]
                counts = [[res[5], res[4]]]
                ellipses = [self._getEllipse(locs[0])]
                self._initial_res.append((locs, counts, ellipses))
            grid_locs = []

        # get initial positions from remaining grid_locs, can be empty
        self._initial_pos = [[self._loc2pos(loc)] for loc in grid_locs]

        # use the 4 corners of the measurement plane to determine the
        # "maximum" estimated travel cost (for normalization in AI)
        corners = [q0, q1, q2, q1 + q2 - q0]
        if not self._initonly:
            session.log.info('Calculating travel costs...')
            cost_sim = self._getTravelCosts([(corners[0], corners[1]),
                                             (corners[2], corners[1]),
                                             (corners[2], corners[3]),
                                             (corners[0], corners[3]),
                                             (corners[0], corners[2]),
                                             (corners[1], corners[3])])
            cost_sim.join()
            if len(cost_sim.results) != 6:
                session.log.warning('Could not calculate travel costs for AI')
                self._travel_cost_max = 1
            else:
                costs = [cost for cost in cost_sim.results
                         if not np.isinf(cost)] + [1]
                self._travel_cost_max = max(costs)
        else:
            self._travel_cost_max = 1

        self._startVisualization()

        QScan.__init__(self, self._initial_pos, firstmoves, [], detlist,
                       envlist, preset, scaninfo, subscan=False)

        self._npoints = maxpts or 0

    def _connect(self, hostport):
        self._socket = nicos_zmq_ctx.socket(zmq.REQ)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.connect('tcp://' + hostport)
        self._poller = zmq.Poller()
        self._poller.register(self._socket, zmq.POLLIN)

    def _request(self, action, **data):
        if self._socket is None:
            return {}
        # send the request
        action = action.encode()

        while True:
            self._socket.send_multipart([self.ID, b'', action,
                                         json.dumps(data).encode()])

            # wait 5 seconds for a response
            for i in range(5):
                events = self._poller.poll(1000)
                if events:
                    break
                if i == 0:
                    session.log.warning('No reply from ARIANE, retrying...')
            else:
                raise CommunicationError('No reply from ARIANE')

            # get the response and decode it
            reply = self._socket.recv_multipart()
            try:
                if len(reply) != 4 or reply[:3] != [self.ID, b'', action]:
                    raise ValueError
                ret_data = json.loads(reply[3].decode())

                # if still busy, retry (without warning)
                if ret_data.get('busy'):
                    session.delay(1)
                    continue

                # if error return, raise immediately
                if not ret_data['success']:
                    raise CommunicationError('Error from ARIANE: %s' %
                                             ret_data['error'])
            except CommunicationError:
                raise
            except Exception as exc:
                raise CommunicationError('Received invalid reply %r' %
                                         reply) from exc
            return ret_data

    def beginScan(self):
        QScan.beginScan(self)

        self._request('reset',
                      mode='single',
                      axes=self._qw.T.tolist(),
                      offset=self._q0.tolist(),
                      limits=self._lim,
                      level_backgr=self._background,
                      thresh_intens=self._int_threshold,
                      travel_cost_max=self._travel_cost_max)
        self._starttime = currenttime()

        for res in self._initial_res:
            self._processResult(*res)

        if not self._initonly:
            self._startpositions = AIPositions(self._initial_pos,
                                               self._requestNextPoint)

    def handleError(self, what, err):
        try:
            QScan.handleError(self, what, err)
        except Exception:
            # we won't get a result, so tell AI not to go here anymore
            if self._last_loc:
                self._reportInaccessible(self._last_loc)
            raise

    def preparePoint(self, num, xvalues):
        # already start calculating the travel costs from the new point
        if not self._initonly:
            curpos = xvalues[0]
            self._travel_cost_sim = self._getTravelCosts([
                (curpos, gridpos) for gridpos in self._posgrid
            ])
        self._preparetime = currenttime()

        QScan.preparePoint(self, num, xvalues)

    def finishPoint(self):
        QScan.finishPoint(self)
        sub = self.dataset.subsets[-1]

        travel_time = sub.started - self._preparetime
        counting_time = sub.finished - sub.started
        times = (travel_time, counting_time)

        try:
            locs, counts, ellipses = self._extractResult(sub)
        except Exception:
            session.log.warning('Could not extract results for AI', exc=1)
        else:
            self._processResult(locs, counts, ellipses, with_cost=True,
                                times=times)

    def endScan(self):
        try:
            QScan.endScan(self)

            if self._initonly:
                # print out background/threshold values from heuristics
                res = self._request('heuris_experi_param')
                session.log.info('Recommended AI cutoffs:')
                if res['level_backgr'] is None:
                    session.log.info('Background: not determined')
                else:
                    session.log.info('Background: %.0f', res['level_backgr'])
                if res['thresh_intens'] is None:
                    session.log.info('Upper threshold: not determined')
                else:
                    session.log.info('Upper threshold: %.0f',
                                     res['thresh_intens'])

            self._request('stop')
        finally:
            self._socket.close()
            self._socket = None

    def shortDesc(self):
        if self.dataset and self.dataset.counter > 0:
            return 'AI-Scan %s/%s #%s' % (self._qw[:, 0], self._qw[:, 1],
                                          self.dataset.counter)
        return 'AI-Scan %s/%s' % (self._qw[:, 0], self._qw[:, 1])

    def _guessPlotIndex(self, _xindex):
        # Basically, there is no good way to make a 1-d plot of this scan
        # anyway. But select an index that doesn't stay constant, so that
        # the plot doesn't appear completely ridiculous.
        for i in range(4):
            if self._qw[i, 0] != 0:
                self._xindex = i
                break

    def _processResult(self, locs, counts, ellipses, with_cost=False, times=(0, 0)):
        kwds = {}
        if with_cost and self._travel_cost_sim:
            self._travel_cost_sim.join()
            costs = self._travel_cost_sim.results
            if len(costs) != len(self._posgrid):
                session.log.warning('Could not calculate travel costs')
                costs = [1] * len(self._posgrid)
            kwds['travel_cost_grid'] = self._locgrid
            kwds['travel_cost_values'] = costs

        kwds['travel_time'], kwds['counting_time'] = times

        self._request('result',
                      locs=locs,
                      counts=counts,
                      matrices_ellipses=ellipses,
                      **kwds)
        self._addVisPoint(locs, counts, ellipses)

    def _requestNextPoint(self, i, retry=20):
        """Called by the iterator to request the next point from AI (the i-th
        point overall).

        Can raise StopIteration if an end condition is reached.
        """
        if self._maxpts and i >= self._maxpts:
            raise StopIteration
        if self._maxtime and currenttime() - self._starttime > self._maxtime:
            raise StopIteration
        if self._socket is None:
            raise StopIteration  # simulation mode: cannot guess anything

        # request the next point
        reply = self._request('next_loc')
        if reply.get('stop'):  # stop request by other side
            raise StopIteration

        loc = self._last_loc = reply['loc']
        pos = self._loc2pos(loc)
        if not session.instrument.isAllowed(pos)[0]:
            session.log.warning('Invalid point requested')
            if retry == 0:
                session.log.warning('Stopping AI scan since no new valid point '
                                    'could be found')
                raise StopIteration
            # tell AI not to go there
            self._reportInaccessible(loc)
            return self._requestNextPoint(i, retry=retry - 1)

        return [pos]

    def _reportInaccessible(self, loc):
        self._request('problem_locs',
                      locs=[loc],
                      matrices_ellipses=[[[(20/self._dlim[0])**2, 0],
                                          [0, (20/self._dlim[1])**2]]])

    def _pos2loc(self, pos):
        # convert position [qx, qy, qz, E] to loc [a, b].
        loc0, loc1 = (self._invqw @ (pos - self._q0))
        # clip to limits to avoid rounding inaccuracies
        return [np.clip(loc0, *self._lim[0]), np.clip(loc1, *self._lim[1])]

    def _loc2pos(self, loc):
        # convert loc [a, b] to position [qx, qy, qz, E].
        return self._q0 + self._qw @ np.array(loc)

    def _getTravelCosts(self, paths):
        # calculate travel costs for a list of (p1, p2) paths
        script = ['from nicos import session', '_tasinstr = session.instrument']
        for (p1, p2) in paths:
            script.extend([
                'try:',
                '  _tasinstr.maw(%s)' % list(p1),
                '  t0 = session.clock.time',
                '  _tasinstr.maw(%s)' % list(p2),
                '  t1 = session.clock.time',
                '  session.log_sender.add_result(t1 - t0)',
                'except:',
                '  session.log_sender.add_result(float("inf"))',
            ])
        return session.runSimulation('\n'.join(script), wait=False,
                                     uuid='ariane', quiet=True)

    def _getEllipse(self, loc):
        # fixed ellipse with 1/50 the axis range in both directions
        return [[(50/self._dlim[0])**2, 0],
                [0, (50/self._dlim[1])**2]]
        # mat = resmat(*_resmat_args(tuple(self._loc2pos(loc)), {}))
        # return (self._qw.T @ mat.NP @ self._qw).tolist()

    # These need to be different for BAMBUS.

    def _isInScanArea(self, ds):
        pos0 = ds.devvaluelist[0:4]
        loc = self._pos2loc(pos0)
        pos1 = self._loc2pos(loc)
        return np.allclose(pos0, pos1, atol=1e-2)

    def _extractResult(self, ds):
        locs = [self._pos2loc(ds.devvaluelist[0:4])]

        monindex = None
        for (i, info) in enumerate(ds.detvalueinfo):
            if info.type == 'monitor':
                monindex = i
                break
        for (i, info) in enumerate(ds.detvalueinfo):
            if info.type == 'counter':
                count = ds.detvaluelist[i]
                if monindex is not None:
                    counts = [[count, ds.detvaluelist[monindex]]]
                else:
                    counts = [[count, 0]]
                break
        else:
            raise UsageError('no counter found in detector results')

        ellipses = [self._getEllipse(locs[0])]

        return locs, counts, ellipses

    # Visualization helpers

    def _startVisualization(self):
        xlabel = str(self._qw[:, 0])
        ylabel = str(self._qw[:, 1])
        if not np.allclose(0, self._q0):
            xlabel = f'{self._q0} + x * {xlabel}'
            ylabel = f'{self._q0} + x * {ylabel}'
        scale = self._dlim[0] / self._dlim[1]
        session.clientExec(make_map, (xlabel, ylabel, True, 1, scale, 50))

    def _addVisPoint(self, locs, counts, ellipses):
        for loc, count in zip(locs, counts):
            z = 1 if not count[1] else (count[0] or 1) / count[1]
            session.clientExec(update_map, (loc[0], loc[1], z))


class AIPositions:
    """Helper iterator to yield the positions to measure at."""

    def __init__(self, initial, request):
        self.i = -1
        self.initial = initial
        self.request = request

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        if self.i < len(self.initial):
            # Still an initial point.
            return self.initial[self.i]
        else:
            # Request the next point from the algorithm.
            return self.request(self.i)


def reduce(vec):
    """Reduce vector into a "unit" vector and scale, if possible."""
    # ensure small values are exactly zero
    vec[np.isclose(0, vec)] = 0.
    # reduce to the smallest nonzero value as unit
    scale = float(np.min(np.abs(vec)[vec != 0]))
    return vec / scale, scale


def determine_axes(q0, q1, q2):
    offset = q0
    lim1l = lim2l = 0.

    # reduce direction vectors
    dir1, lim1h = reduce(q1 - q0)
    dir2, lim2h = reduce(q2 - q0)

    # try to express offset in terms of direction vectors
    sol, resid, *_ = np.linalg.lstsq(np.array([dir1, dir2]).T, q0, rcond=None)
    if np.allclose(0, resid):
        sol = sol.round(4)
        offset = np.zeros(4)
        lim1l, lim2l = sol
        lim1h += lim1l
        lim2h += lim2l

    # sanity check
    assert np.allclose(q0, offset + dir1 * lim1l + dir2 * lim2l)
    assert np.allclose(q1, offset + dir1 * lim1h + dir2 * lim2l)
    assert np.allclose(q2, offset + dir1 * lim1l + dir2 * lim2h)

    # fix ordering of limits if necessary
    if lim1l > lim1h:
        lim1l, lim1h = lim1h, lim1l
    if lim2l > lim2h:
        lim2l, lim2h = lim2h, lim2l

    return offset, dir1, [lim1l, lim1h], dir2, [lim2l, lim2h]
