#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Slit device for SPODI/STRESSI with multiplexed motors."""

from nicos.core import MoveError, SIMULATION
from nicos.devices.generic import Slit as GenericSlit, TwoAxisSlit as \
    GenericTwoAxisSlit
from nicos.devices.generic.sequence import SequencerMixin, SeqDev


class Slit(SequencerMixin, GenericSlit):

    def _doStartPositions(self, positions):
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])

        f = self.coordinates == 'opposite' and -1 or +1
        tl, tr, tb, tt = positions
        # determine which axes to move first, so that the blades can
        # not touch when one moves first
        cl, cr, cb, ct = [d.read(0) for d in self._axes]
        cl *= f
        cb *= f
        al, ar, ab, at = self._axes
        seq = []
        if tr < cr and tl < cl:
            # both move to smaller values, need to start right blade first
            seq.append(SeqDev(al, tl * f))
            seq.append(SeqDev(ar, tr))
        elif tr > cr and tl > cl:
            # both move to larger values, need to start left blade first
            seq.append(SeqDev(ar, tr))
            seq.append(SeqDev(al, tl * f))
        else:
            # don't care
            seq.append(SeqDev(ar, tr))
            seq.append(SeqDev(al, tl * f))
        if tb < cb and tt < ct:
            seq.append(SeqDev(ab, tb * f))
            seq.append(SeqDev(at, tt))
        elif tb > cb and tt > ct:
            seq.append(SeqDev(at, tt))
            seq.append(SeqDev(ab, tb * f))
        else:
            seq.append(SeqDev(at, tt))
            seq.append(SeqDev(ab, tb * f))

        self._startSequence(seq)


class TwoAxisSlit(SequencerMixin, GenericTwoAxisSlit):

    def doStart(self, target):
        th, tv = target

        seq = []
        seq.append(SeqDev(self._attached_horizontal, th))
        seq.append(SeqDev(self._attached_vertical, tv))

        self._startSequence(seq)
