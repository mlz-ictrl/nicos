# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************
"""PUMA Monochromator changer."""

from nicos import session
from nicos.core import Attach, Moveable, Param, PositionError, Readable, \
    anytype, dictof, multiWait, oneof


class Mchanger(Moveable):
    """PUMA specific monochromator changer device."""

    attached_devices = {
        'monochromator': Attach('Monochromator', Moveable),
        'magazine': Attach('Magazine', Moveable),
        'r3': Attach('3R coupling', Moveable),
        'lift': Attach('Lift', Moveable),
        'grip': Attach('Grip', Moveable),
        'mlock': Attach('Magnetic lock', Moveable),
        'holdstat': Attach('Read status of monochromators holders of the '
                           'magazine', Readable),
        'focush': Attach('Horizontal focusing', Moveable),
        'focusv': Attach('Vertical focusing', Moveable),
        'mono_stat': Attach('Read status of monochromators on the monotable',
                            Moveable),
    }

    parameters = {
        'changing_positions': Param('Dictionary of devices and positions '
                                    'for monochromator change', mandatory=True,
                                    type=dictof(str, anytype), settable=False),
        'init_positions': Param('Dictionary of devices and positions '
                                'for monochromator start', mandatory=True,
                                type=dictof(str, anytype), settable=False),
        'mapping': Param('Mapping of valid Changer states to '
                         'monochromatordevice used in that state',
                         type=dictof(str, str), mandatory=True,
                         settable=False),
    }

    hardware_access = False

    def doInit(self, mode):
        # self._switchlist = self._attached_holdstat._iolist.keys()
        # self.valuetype = oneof(*self._switchlist)
        self.valuetype = oneof(*self.mapping)
        # replaced devicename by device and make a local copy
        devices = list(self.changing_positions)
        self._changing_values = dict(zip(map(session.getDevice, devices),
                                         self.changing_positions.values()))
        devices = list(self.init_positions)
        self._init_values = dict(zip(map(session.getDevice, devices),
                                     self.init_positions.values()))

    def doStart(self, target):
        try:
            curpos = self.doRead(0)
            if self.isAtTarget(curpos, target=target):
                self.log.info('%s is already in the beam.', target)
                return
            self._move2start()
        except PositionError:
            self.log.info('Cannot start monochromator change')
            raise

        if curpos != 'None':
            self.log.info('Remove %s', curpos)
            self._focusOut()
            self._change_alias('None')
            self._moveUp(curpos)

        # now curpos is 'None' ....
        if target != 'None':
            self.log.info('Put down %s', target)
            self._moveDown(target)
            self._change_alias(target)
            self._focusOn()
        self._finalize()

    def doRead(self, maxage=0):
        up = self._attached_holdstat.read(maxage)
        if up not in ('None', self._attached_mono_stat.read(maxage)):
            raise PositionError(self, 'unknown position of %s' % self.name)
        return up

    def doIsAllowed(self, pos):
        if self._attached_lift.read(0) != 'ref':
            return (False, 'Lift is not at reference position. Please check if'
                    ' mono is fixed at the magazine or at the monotable')
        return True, ''

    def _move2start(self):
        self.log.info('Move %s for monochromator change',
                      ', '.join(sorted(self.changing_positions)))

        for dev, pos in self._changing_values.items():
            dev.start(pos)

        # multiWait(self._changing_values)
        multiWait(self._changing_values.keys())

        for dev, pos in self._changing_values.items():
            if abs(dev.read(0) - pos) > dev.precision:
                raise PositionError(self, "'%s' did not reach target position "
                                    "'%s'" % (dev, pos))

        for dev in self._changing_values:
            dev.fix('Monochromator change in progress')
        # may block change of alias!
        # self._attached_monochromator.fix('Monochromator change in progress')

        # test this!
        # self.log.debug('Disabling Powerstages for %s',
        #                ', '.join(sorted(self.changing_positions)))
        # for dev in self.changing_positions:
        #     dev.power = 'off'

    def _focusOut(self):
        self.log.info('Focusing to the flat position is temporarily disabled')
        aliasdevice = self._attached_monochromator
        foch = session.getDevice(aliasdevice.alias)._attached_focush
        focv = session.getDevice(aliasdevice.alias)._attached_focusv
        # if foch is not None:
        #     foch.start(0)
        # if focv is not None:
        #     focv.start(0)
        # if foch is not None:
        #     foch.wait()
        # if focv is not None:
        #     focv.wait()
        self.log.info('Switch off the focush and focusv motors')
        if focv is not None:
            focv.motor.power = 'off'
        if foch is not None:
            foch.motor.power = 'off'

    def _focusOn(self):
        aliasdevice = self._attached_monochromator
        foch = session.getDevice(aliasdevice.alias)._attached_focush
        focv = session.getDevice(aliasdevice.alias)._attached_focusv
        self.log.info('Switch on the focush and focusv motors')
        if focv is not None:
            focv.motor.power = 'on'
        if foch is not None:
            foch.motor.power = 'on'

    def _finalize(self):
        """Will be called after a successful monochromator change."""
        # test this!
        # self.log.debug('Enabling Powerstages for %s',
        #                ', '.join(sorted(self.changing_positions)))
        # for dev in self._changing_values:
        #     dev.power = 'on'

        self.log.info('releasing mono devices')
        # self._attached_monochromator.release()
        for dev in self._changing_values:
            dev.release()
        self.log.info('move mono devices to the nominal positions')
        for dev, pos in self._init_values.items():
            dev.start(pos)

        multiWait(self._init_values.keys())

        for dev, pos in self._init_values.items():
            if abs(dev.read(0) - pos) > dev.precision:
                raise PositionError(self, "'%s' did not reach target position "
                                    "'%s'" % (dev, pos))

    def _moveUp(self, pos):
        self._step('magazine', pos)
        self._step('grip', 'open')
        self._step('lift', 'bottom')
        self._step('grip', 'closed')
        self._step('r3', 'open')
        self._step('mlock', 'open')
        self._step('lift', 'top2')
        self._step('mlock', 'closed')
        self._step('lift', 'top1')
        self._step('grip', 'open')
        self._step('lift', 'ref')
        self._step('grip', 'closed')

    def _moveDown(self, pos):
        self._step('magazine', pos)
        self._step('grip', 'open')
        self._step('lift', 'top1')
        self._step('grip', 'closed')
        self._step('lift', 'top2')
        self._step('mlock', 'open')
        self._step('r3', 'open')
        self._step('lift', 'bottom')
        self._step('r3', 'closed')
        self._step('grip', 'open')
        self._step('lift', 'ref')
        self._step('grip', 'closed')
        self._step('mlock', 'closed')

    def _change_alias(self, pos):
        """Change the alias of the monochromator DeviceAlias."""
        aliastarget = self.mapping.get(pos, None)
        aliasdevice = self._attached_monochromator
        if aliastarget and hasattr(aliasdevice, 'alias'):
            self.log.info('switching alias %r to %r', aliasdevice, aliastarget)
            aliasdevice.alias = session.getDevice(aliastarget)
        else:
            self.log.info('NOT changing Aliasdevice')

    def _step(self, devicename, pos):
        """Make one step in the changing sequence.

        Evaluates the given keyword argument and
        moves the attached_device with the keyname to the value-position.
        Also checks success
        """
        dev = self._adevs[devicename]
        # now log some info
        if pos == 'open':
            self.log.info('Open %r', dev.name)
        elif pos == 'closed':
            self.log.info('Close %r', dev.name)
        else:
            self.log.info('Move %r to %r position', dev.name, pos)
        try:
            dev.start(pos)
            if devicename == 'r3':  # R3 does not wait!
                session.delay(2)
            if devicename == 'grip':  # grip does not wait!
                session.delay(2)
            dev.wait()
        except Exception:
            # most probably it is touching the limit switch
            if devicename == 'lift':
                dev._adevs['moveables'][0].motor.stop()
                self.log.info('Limit switch ?')
            else:
                raise
        if dev.read(0) != pos:
            raise PositionError(
                self, 'Device %r did not reach its target %r, aborting' % (
                    dev, pos))
