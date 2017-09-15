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
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA Monochromator changer hardware classes. FOR TESTING ONLY!"""

from nicos import session
from nicos.core import Readable, Moveable, status, usermethod
from nicos.core.device import HasOffset
from nicos.core.utils import multiWait
from nicos.core.params import Param, Override, Attach, oneof
from nicos.core.errors import MoveError, NicosError, UsageError
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod, \
    SequenceItem, SeqCall


class HWError(NicosError):
    category = 'Hardware error'  # can't continue!


#
# new SequenceItems
#
class SeqCheckStatus(SequenceItem):
    def __init__(self, dev, status, *args, **kwargs):
        SequenceItem.__init__(self, dev=dev, status=status, args=args, kwargs=kwargs)

    def run(self):
        if hasattr(self.status, '__iter__'):
            stati = self.status
        else:
            stati = [self.status]
        status = self.dev.status(0)[0]
        if status not in stati:
            raise HWError('Expected %r to have a Status of %r, but has '
                          '%r' % (self.dev, stati, status))


class SeqCheckPosition(SequenceItem):
    def __init__(self, dev, position, *args, **kwargs):
        SequenceItem.__init__(self, dev=dev, position=position, args=args,
                              kwargs=kwargs)

    def run(self):
        if hasattr(self.position, '__iter__'):
            positions = self.position
        else:
            positions = [self.position]
        pos = self.dev.read(0)
        if pos not in positions:
            raise HWError('Expected %r to have a Position of %r, but '
                          'has %r' % (self.dev, positions, pos))


class SeqSetAttr(SequenceItem):
    def __init__(self, obj, key, value):
        SequenceItem.__init__(self, obj=obj, key=key, value=value)

    def run(self):
        setattr(self.obj, self.key, self.value)


class SeqCheckAttr(SequenceItem):
    def __init__(self, obj, key, value=None, values=None):
        SequenceItem.__init__(self, obj=obj, key=key, value=value, values=values)

    def run(self):
        if self.value is not None:
            if getattr(self.obj, self.key) != self.value:
                raise HWError('%s.%s should be %r !' %
                              (self.obj, self.key, self.value))
        elif self.values is not None:
            if getattr(self.obj, self.key) not in self.values:
                raise HWError('%s.%s should be one of %s !'
                              % (self.obj, self.key, ', '.join(self.values)))


#
# here comes the real monochanger device: TEST THIS !
#
class Changer(BaseSequencer):
    attached_devices = {
        'lift':           Attach('Lift moving a mono up or down between 4 '
                                 'positions', Moveable),
        'magazine':       Attach('Magazine holding the monos and having 4 '
                                 'positions', Moveable),
        'liftclamp':      Attach('Clamp holding the mono in the lift',
                                 Moveable),
        'magazineclamp':  Attach('Clamp holding the mono in the magazine',
                                 Moveable),
        'tableclamp':     Attach('Clamp holding the mono on the table',
                                 Moveable),
        'inhibitrelay':   Attach('Inhibit to the remaining motor controllers',
                                 Moveable),
        'enable':         Attach('To enable operation of the changer',
                                 Moveable),
        'magazineocc':    Attach('Readout for occupancy of the magazine',
                                 Readable),
        'magazinestatus': Attach('Readout for status of magazine load position',
                                 Readable),
    }

    parameters = {
        'mono_on_table':   Param('Name of Mono on the Monotable',
                                 type=oneof('PG', 'Si', 'Cu', 'Heusler',
                                            'None', 'empty frame'),
                                 default='None', settable=True, userparam=False),
        'mono_in_lift':    Param('Which mono is in the lift',
                                 type=oneof('PG', 'Si', 'Cu', 'Heusler',
                                            'None', 'empty frame'),
                                 default='None', settable=True, userparam=False),
        'exchangepos':     Param('dict of device names to positional values '
                                 'for changing monos',
                                 type=dict, settable=False, userparam=False),
        'precisionchange': Param('dict of device names and pairs of (normal '
                                 'value, change value) of the precision',
                                 type=dict, settable=False, userparam=False),
    }

    parameter_overrides = {
        'requires': Override(default={'level': 'admin'}),
    }

    positions = ['101', '110', '011', '111']  # CounterClockwise
    monos = ['Heusler', 'PG', 'Si', 'empty frame']  # assigned monos
    shields = ['110', '110', '110', '110']  # which magzinslot after changing
    #    (e.g. Put a PE dummy to 101 and set this to ('101,'*4).split(',')
    valuetype = oneof(*(monos + ['None']))

    def PrepareChange(self):
        '''is checking whether all the conditions for a change of mono are met'''

        # if not(self.SecShutter_is_closed()):
        #     raise UsageError(self, 'Secondary Shutter needs to be closed, '
        #                      'please close by hand and retry!')
        # if self.NotAus():
        #     raise UsageError(self, 'NotAus (Emergency stop) activated, '
        #                      'please check and retry!')
        # read all inputs and check for problems
        if not(self._attached_magazine.read() in self.positions):
            raise HWError(self, 'Unknown Magazine-Position !')
        if self._attached_lift.read() != '2':
            raise HWError(self, 'Lift not at parking position!')
        if self._attached_liftclamp.read() != 'close':
            raise HWError(self, 'liftclamp should be closed!')
        if self._attached_tableclamp.read() != 'close':
            raise HWError(self, 'tableclamp should be closed!')
        if self._attached_magazineclamp.read() != 'close':
            raise HWError(self, 'magazineclamp should be closed!')
        if self.mono_in_lift != 'None':
            raise HWError(self, 'There is mono %s in the lift, please change '
                                'manually!' % self.mono_in_lift)

        # XXX TODO: store old values of positions and offsets someplace to
        # recover after changing back
        self.log.info('will change position of several devices to the '
                      'changing position, moving back is not yet implemented')

        # enhance precision of the devices
        for devname, prec in self.precisionchange.items():
            dev = session.getDevice(devname)
            dev.precision = prec[1]
            self.log.debug('changing precision of the %s device to the %f',
                           devname, prec[1])

        # go to the place where a change is possible
        devs = []
        for devname, pos in self.exchangepos.items():
            dev = session.getDevice(devname)
            # remove after implementation of moving back
            self.log.info('position of the %s device was %f', devname, dev())
            if isinstance(dev, HasOffset):
                dev.start(pos - dev.offset)
                self.log.debug('move and wait %s to the position %f - offset of %f',
                               devname, pos, dev.offset)
                dev.wait()
            else:
                dev.start(pos)
                self.log.debug('move and wait %s to the position %f', devname, pos)
                dev.wait()
            devs.append(dev)
        multiWait(devs)

        # put precision back to normal
        for devname, prec in self.precisionchange.items():
            dev = session.getDevice(devname)
            dev.precision = prec[0]
            self.log.debug('changing precision of the %s device back to '
                           'the %f', devname, prec[0])

        try:
            dev = session.getDevice('focibox')
            self.mono_on_table = dev.read(0)
            dev.comm('XMA', forcechannel=False)
            dev.comm('YMA', forcechannel=False)
            dev.driverenable = False
            self.log.info('focus motors disabled')
        except NicosError as err:
            self.log.error('Problem disabling foci: %s', err)

        # switch on inhibit and enable
        self._attached_enable.maw(0xef16)
        self._attached_inhibitrelay.maw('on')
        self.log.info('changer enabled and inhibit active')

    def FinishChange(self):
        self._attached_inhibitrelay.maw('off')
        self._attached_enable.maw(0)
        self.log.warning('Please restart the daemon or reload the setups to '
                         'init the new Mono:')
        self.log.warning('  > NewSetup()')
        self.log.info('  > NewSetup()')

    def CheckMagazinSlotEmpty(self, slot):
        # checks if the given slot in the magazin is empty
        self.log.info('checking of there IS NOT mono in magazine slot %r' % slot)
        if self._attached_magazineocc.status(0)[0] != status.OK:
            raise UsageError(self, 'Magazine occupancy switches are in warning state!')
        index = self.positions.index(slot)
        if not((self._attached_magazineocc.read() >> index*2) & 1):
            raise UsageError(self, 'Position %r is already occupied!' % slot)

    def CheckMagazinSlotUsed(self, slot):
        # checks if the given slot in the magazin is used (contains a monoframe)
        self.log.info('checking of there IS mono in magazine slot %r' % slot)
        if self._attached_magazineocc.status(0)[0] != status.OK:
            raise UsageError(self, 'Magazine occupancy switches are in warning state!')
        index = self.positions.index(slot)
        if (self._attached_magazineocc.read() >> index*2) & 1:
            raise UsageError(self, 'Position %r is empty!' % slot)

    def _start(self, seq):
        if self._seq_is_running():
            raise MoveError(self, 'Can not start sequence, device is still '
                            'busy')
        self._startSequence(seq)

    # here is the party going on!
    def Transfer_Mono_Magazin2Lift(self):
        self._start(self._gen_mag2lift())
        self.wait()

    def _gen_mag2lift(self, magpos=None):
        seq = []
        if magpos is None:
            magpos = self._attached_magazine.read(0)
        else:
            seq.append(SeqDev(self._attached_magazine, magpos))
        # check preconditions
        seq.append(SeqCall(self.log.info, 'checking preconditions for Magazin2Lift'))
        seq.append(SeqCheckStatus(self._attached_magazine, status.OK))
        seq.append(SeqCheckStatus(self._attached_lift, status.OK))
        seq.append(SeqCheckPosition(self._attached_lift, '2'))
        seq.append(SeqCheckPosition(self._attached_liftclamp, 'close'))
        seq.append(SeqCheckPosition(self._attached_magazine, magpos))
        seq.append(SeqCheckPosition(self._attached_magazineclamp, 'close'))
        seq.append(SeqMethod(self, 'CheckMagazinSlotUsed', magpos))
        seq.append(SeqCheckAttr(self, 'mono_in_lift', 'None'))
        # transfer mono to lift
        seq.append(SeqCall(self.log.info, 'transfering mono from magazine to lift'))
        seq.append(SeqDev(self._attached_liftclamp, 'open'))
        seq.append(SeqDev(self._attached_lift, '3'))  # almost top position
        seq.append(SeqMethod(self._attached_liftclamp, 'start', 'close'))
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqDev(self._attached_liftclamp, 'close'))
        seq.append(SeqMethod(self._attached_magazineclamp, 'start', 'open'))
        # rattle a little
        seq.append(SeqCall(self.log.info, 'rattle to release magazine grab'))
        seq.append(SeqDev(self._attached_lift, '3'))  # almost top position
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqDev(self._attached_lift, '3'))  # almost top position
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqDev(self._attached_magazineclamp, 'open'))
        seq.append(SeqMethod(self, 'CheckMagazinSlotEmpty', magpos))
        # move (with mono) to parking position
        seq.append(SeqCall(self.log.info, 'moving with mono to parking position'))
        seq.append(SeqSetAttr(self, 'mono_in_lift',
                              self.monos[self.positions.index(magpos)]))
        seq.append(SeqDev(self._attached_lift, '2'))  # park position
        seq.append(SeqDev(self._attached_magazineclamp, 'close'))
        # Magazin should not contain a mono now
        seq.append(SeqMethod(self, 'CheckMagazinSlotEmpty', magpos))
        return seq

    def Transfer_Mono_Lift2Magazin(self):
        self._start(self._gen_lift2mag())
        self.wait()

    def _gen_lift2mag(self, magpos=None):
        seq = []
        if magpos is None:
            magpos = self._attached_magazine.read(0)
        else:
            seq.append(SeqDev(self._attached_magazine, magpos))
        # check preconditions
        seq.append(SeqCall(self.log.info, 'checking preconditions for Lift2Magazin'))
        seq.append(SeqCheckStatus(self._attached_magazine, status.OK))
        seq.append(SeqCheckStatus(self._attached_lift, status.OK))
        seq.append(SeqCheckPosition(self._attached_lift, '2'))
        seq.append(SeqCheckPosition(self._attached_liftclamp, 'close'))
        seq.append(SeqCheckPosition(self._attached_magazine, magpos))
        seq.append(SeqCheckPosition(self._attached_magazineclamp, 'close'))
        seq.append(SeqMethod(self, 'CheckMagazinSlotEmpty', magpos))
        # there needs to be a mono in the lift
        seq.append(SeqCall(self.log.info, 'checking if there is a mono in lift'))
        seq.append(SeqCheckAttr(self, 'mono_in_lift',
                                values=[m for m in self.monos if m != 'None']))
        # prepare magazin
        seq.append(SeqCall(self.log.info, 'testing magazin grab'))
        seq.append(SeqDev(self._attached_magazineclamp, 'open'))
        seq.append(SeqDev(self._attached_magazineclamp, 'close'))
        seq.append(SeqDev(self._attached_magazineclamp, 'open'))
        seq.append(SeqDev(self._attached_magazineclamp, 'close'))
        seq.append(SeqDev(self._attached_magazineclamp, 'open'))
        # transfer mono to lift
        seq.append(SeqCall(self.log.info, 'moving lift to top position'))
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqCall(self.log.info, 'closing the magazin grab anf rattling lift'))
        seq.append(SeqMethod(self._attached_magazineclamp, 'start', 'close'))
        # rattle a little
        seq.append(SeqDev(self._attached_lift, '3'))  # almost top position
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqDev(self._attached_lift, '3'))  # almost top position
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqDev(self._attached_lift, '3'))  # almost top position
        seq.append(SeqDev(self._attached_magazineclamp, 'close'))
        seq.append(SeqMethod(self, 'CheckMagazinSlotUsed', magpos))
        seq.append(SeqCall(self.log.info, 'opening lift clamp'))
        seq.append(SeqMethod(self._attached_liftclamp, 'start', 'open'))
        seq.append(SeqDev(self._attached_lift, '4'))  # top position
        seq.append(SeqDev(self._attached_lift, '3'))  # top position
        seq.append(SeqDev(self._attached_liftclamp, 'open'))
        seq.append(SeqCall(self.log.info, 'moving lift to park position'))
        seq.append(SeqDev(self._attached_lift, '2'))  # park position
        seq.append(SeqCall(self.log.info, 'closing lift clamp'))
        seq.append(SeqDev(self._attached_liftclamp, 'close'))
        # move (without mono) to parking position
        seq.append(SeqSetAttr(self, 'mono_in_lift', 'None'))
        # Magazin should not contain a mono now
        seq.append(SeqMethod(self, 'CheckMagazinSlotUsed', magpos))
        return seq

    def Transfer_Mono_Lift2Table(self):
        self._start(self._gen_lift2table())
        self.wait()

    def _gen_lift2table(self):
        seq = []
        # check preconditions
        seq.append(SeqCall(self.log.info, 'checking preconditions for Lift2Table'))
        seq.append(SeqCheckStatus(self._attached_tableclamp, status.OK))
        seq.append(SeqCheckStatus(self._attached_liftclamp, status.OK))
        seq.append(SeqCheckStatus(self._attached_lift, status.OK))
        seq.append(SeqCheckPosition(self._attached_lift, '2'))
        seq.append(SeqCheckPosition(self._attached_liftclamp, 'close'))
        seq.append(SeqCheckPosition(self._attached_tableclamp, 'close'))
        # there shall be a mono in the lift!
        seq.append(SeqCall(self.log.info, 'check if there is a mono in Lift'))
        seq.append(SeqCheckAttr(self, 'mono_in_lift',
                                values=[m for m in self.monos if m != 'None'])
                   )
        seq.append(SeqCheckAttr(self, 'mono_on_table', 'None'))
        seq.append(SeqCall(self.log.info, 'moving down the lift'))
        # transfer mono to table
        seq.append(SeqDev(self._attached_tableclamp, 'open'))
        seq.append(SeqDev(self._attached_lift, '1'))  # bottom position
        seq.append(SeqCall(self.log.info, 'closing Table grab and releasing lift clamp'))
        seq.append(SeqDev(self._attached_tableclamp, 'close'))
        # move (without mono) to parking position
        seq.append(SeqDev(self._attached_liftclamp, 'open'))

        def func(self):
            self.mono_on_table, self.mono_in_lift = self.mono_in_lift, 'None'
        seq.append(SeqCall(func, self))
        # seq.append(SeqSetAttr(self, 'mono_on_table', self.mono_in_lift))
        # seq.append(SeqSetAttr(self, 'mono_in_lift', 'None'))
        seq.append(SeqCall(self.log.info, 'moving lift to park position'))
        seq.append(SeqDev(self._attached_lift, '2'))  # park position
        seq.append(SeqDev(self._attached_liftclamp, 'close'))
        # TODO: change foci alias and reactivate foci
        return seq

    def Transfer_Mono_Table2Lift(self):
        self._start(self._gen_table2lift())
        self.wait()

    def _gen_table2lift(self):
        # XXX TODO drive all foci to 0 and switch of motors....
        # XXX TODO move mty/mtx to monospecific abholposition
        # hier nur das reine abholen vom Monotisch
        seq = []
        # check preconditions
        seq.append(SeqCall(self.log.info, 'checking preconditions for Table2Lift'))
        seq.append(SeqCheckStatus(self._attached_tableclamp, status.OK))
        seq.append(SeqCheckStatus(self._attached_liftclamp, status.OK))
        seq.append(SeqCheckStatus(self._attached_lift, status.OK))
        seq.append(SeqCheckPosition(self._attached_lift, '2'))
        seq.append(SeqCheckPosition(self._attached_liftclamp, 'close'))
        seq.append(SeqCheckPosition(self._attached_tableclamp, 'close'))
        # there shall be no mono in the lift, but one on the table
        seq.append(SeqCall(self.log.info, 'check if there IS NOT a mono in Lift'))
        seq.append(SeqCheckAttr(self, 'mono_in_lift', 'None'))
        seq.append(SeqCheckAttr(self, 'mono_on_table',
                                values=[m for m in self.monos if m != 'None']))
        # transfer mono to lift
        seq.append(SeqCall(self.log.info, 'moving down the lift'))
        seq.append(SeqDev(self._attached_liftclamp, 'open'))
        seq.append(SeqDev(self._attached_lift, '1'))  # bottom position
        seq.append(SeqCall(self.log.info, 'grabing the monochromator'))
        seq.append(SeqDev(self._attached_liftclamp, 'close'))
        seq.append(SeqDev(self._attached_tableclamp, 'open'))

        # move (with mono) to parking position
        def func(self):
            self.mono_on_table, self.mono_in_lift = 'None', self.mono_on_table
        seq.append(SeqCall(func, self))
        # seq.append(SeqSetAttr(self, 'mono_on_table', 'None'))
        # seq.append(SeqSetAttr(self, 'mono_in_lift', self.mono_on_table))
        seq.append(SeqCall(self.log.info, 'moving the lift with mono to parking position'))
        seq.append(SeqDev(self._attached_lift, '2'))  # park position
        seq.append(SeqDev(self._attached_tableclamp, 'close'))
        return seq

    def doStart(self, target):
        self.change(self.mono_on_table, target)

    def change(self, old, whereto):
        ''' cool kurze Wechselroutine
        Der Knackpunkt ist in den Hilfsroutinen!'''
        if not(old in self.monos + ['None']):
            raise UsageError(self, '\'%s\' is illegal value for Mono, use one '
                             'of ' % old + ', '.join(self.monos + ['None']))
        if not(whereto in self.monos + ['None']):
            raise UsageError(self, '\'%s\' is illegal value for Mono, use one '
                             'of ' % whereto + ', '.join(self.monos + ['None'])
                             )
        self.PrepareChange()
        if self.monos.index(whereto) == self.monos.index(old):
            # Nothing to do, requested Mono is supposed to be on the table
            return
        # Ok, we have a good state, the only thing we do not know is which mono
        # is on the table......
        # for this we use the (cached) parameter mono_on_table

        if self.mono_on_table != old:
            raise UsageError(self, 'Mono %s is not supposed to be on the '
                             'table, %s is!' % (old, self.mono_on_table))

        seq = []
        # 0) move magazine to mono position
        magpos_to_put = self.positions[self.monos.index(old)]
        seq.append(SeqMethod(self, 'CheckMagazinSlotEmpty', magpos_to_put))
        seq.append(SeqDev(self._attached_magazine, magpos_to_put))
        # 1) move away the old mono, if any
        if old != 'None':
            seq.extend(self._gen_table2lift())
            seq.extend(self._gen_lift2mag(self.positions[
                self.monos.index(old)]))
        # 2) fetch the new mono (if any) from the magazin
        if whereto != 'None':
            seq.extend(self._gen_mag2lift(self.positions[
                self.monos.index(whereto)]))
            seq.extend(self._gen_lift2table())
            seq.append(SeqDev(self._attached_magazine,
                              self.shields[self.monos.index(whereto)]))

        # seq.append(SeqDev(self._attached_enable, 0)) - will be done in FinishChange
        seq.append(SeqMethod(self, 'FinishChange'))
        self._start(seq)
        self.wait()

    @usermethod
    def printstatusinfo(self):
        self.log.info('PLC is %s',
                      'enabled' if self._attached_enable.read() == 0xef16
                      else 'disabled, you need to set enable_word to correct value')
        self.log.info('Inhibit_relay is %s', self._attached_inhibitrelay.read())
        liftposnames = {'1': 'Monotable loading',
                        '2': 'Park position',
                        '3': 'Bottom storage',
                        '4': 'Upper storage'}
        self.log.info('lift is at %s', liftposnames[self._attached_lift.read()])
        try:
            magpos = self._attached_magazine.read()
            self.log.info('magazine is at %r which is assigned to %s',
                          magpos, self.monos[self.positions.index(magpos)])
        except Exception:
            self.log.error('magazine is at an unknown position !!!')
        for n in 'liftclamp magazineclamp tableclamp'.split():
            self.log.info('%s is %s', n, self._adevs[n].read())
        occ = self._attached_magazineocc.read(0)
        for i in range(4):
            self.log.info('magazineslot %r is %sempty and its readouts are %sbroken',
                          self.positions[i],
                          '' if (occ >> (i*2)) & 1 else 'not ',
                          '' if (occ >> (i*2 + 1)) & 1 else 'not ')
        if self._attached_magazinestatus.read() == 'free':
            self.log.info('Magazine is currently free to load monochromator')
        else:
            self.log.info('Magazine is currently occupied with monochromator '
                          'and cannot load another')

    def doRead(self, maxage=0):
        return ''
