from nicos.core import Attach, InvalidValueError, Moveable, MoveError, \
    Override, anytype, dictof, floatrange, multiWait, tupleof
from nicos.core.constants import SIMULATION
from nicos.devices.generic import MultiSwitcher
from nicos.devices.generic.sequence import SeqMethod, SequencerMixin


class OpticToolSwitch(SequencerMixin, MultiSwitcher):
    """Three-state device for Optic tool

    The optic tool (where pinholes or other optics can be mounted) has three
    general positions important for the user: between X-ray source and sample,
    or between sample and detector (actually two positions since detector can
    operate in transmission or reflection mode).

               Det
        ________________
        |               |           .-->x
        |  .--->2<---.  |           |
        |  |         |  |           v
        |  v         v  |           y
    Det |  3    S    1  |<--- Beam
        |               |
        |_______________|

    Top view on sample chamber, important positions for optics at 1,2,3,
    Detector positions Det, Sample position S. In order to not hit sample
    with the optics they have to move around the sample (MoveFirstX and
    MoveFirstY take care of that).
    """
    attached_devices = {
        'moveables': Attach('The 3 (continuous) devices which are'
                            ' controlled', Moveable, multiple=3),
    }

    parameter_overrides = {
        'mapping':   Override(description='Mapping of state names to 3 values '
                              'to move the moveables to',
                              type=dictof(anytype,
                                          tupleof(float, float, float))),

        'precision': Override(description='List of allowed deviations from '
                                          'target position', mandatory=True,
                                          type=tupleof(floatrange(0),
                                                       floatrange(0),
                                                       floatrange(0))),
    }

    def doStart(self, target):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence(target))``
        """
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(target))

    def _generateSequence(self, target):
        curpos = self.read(0)
        if target == curpos:
            return []

        if target == 2:
            return [SeqMethod(self, '_moveFirstY', target)]

        elif curpos == 2:
            return [SeqMethod(self, '_moveFirstX', target)]

        elif curpos in [1, 3]:
            return [SeqMethod(self, '_moveFirstY', 2),
                    SeqMethod(self, '_moveFirstX', target)]

        raise MoveError(
            self, 'Ended up in an unknown position (at %s)' % curpos)

    def _moveFirstX(self, target):
        self.log.debug('Tx is moved first to avoid '
                       'collision, then go to %s', target)
        moveables = self._attached_moveables
        self._startRaw(self._mapTargetValue(target), moveables)

    def _moveFirstY(self, target):
        self.log.debug('Ty is moved first to avoid '
                       'collision, then go to %s', target)
        values = self._mapTargetValue(target)
        moveables = [self._attached_moveables[1],
                     self._attached_moveables[0], self._attached_moveables[2]]
        self._startRaw([values[1], values[0], values[2]], moveables)

    def _startRaw(self, target, moveables):
        """target is the raw value, i.e. a list of positions"""
        if not isinstance(target, (tuple, list)) or \
                len(target) < len(moveables):
            raise InvalidValueError(self, 'doStart needs a tuple of %d '
                                    'positions for this device!' %
                                    len(moveables))
        # only check and move the moveables, which are first in self.devices
        for d, t in zip(moveables, target):
            if not d.isAllowed(t):
                raise InvalidValueError(self, 'target value %r not accepted '
                                        'by device %s' % (t, d.name))
        for d, t in zip(moveables, target):
            self.log.debug('moving %r to %r', d, t)
            d.maw(t)
        if self.blockingmove:
            multiWait(moveables)
