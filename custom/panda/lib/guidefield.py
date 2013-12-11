# Polarized support for Panda
# (c) 2009 by Enrico Faulhaber
# put under GPLv2 Licence
#
# v0.5
# uses a MappedMoveable now
#
# v0.4
# Now works with the new generic.Switcher as base
# alphastorage also updates the guidefield whenever the tas-device moves
#
# v0.3
# changes:
# works now as a switchable, every switch request sets the correct field
# still some minor problems
#
# v0.2
# changes:
# works in panda as a moveable
# setmode sets the operation mode
# TODO: change to a switchable, which determines needed values autonomous
#
# v0.1alpha
# based on setfield.py
# changes:
# implemented as Class GuideField
# support for pandacontrol-interface (doStart,doRead,...)
# current-limits for coils are now taken from the
#     correspondig coil-object(s)
# suggestion for a nicm_conf.py entry


import numpy as np

from nicos.utils import lazy_property
from nicos.core import Moveable, Param, Override, LimitError, \
    InvalidValueError, multiStop, multiStatus
from nicos.core.params import nonemptylistof, floatrange, tupleof
from nicos.devices.generic import VirtualMotor
from nicos.devices.abstract import MappedMoveable
#~ from nicos.devices.taco import CurrentSupply
from nicos.devices.taco.io import AnalogOutput


################################################################################
# configuration
# 'orient' gives the field produced by coil i (i=0,1,2) by 'current' in XYZ
# coordinates fixed to the spectrometer limits are currently given here too....
# 'driver' is the name of an object controlling that particular coil:
# - X is parallel to the incoming neutrons (X~ki)
# - Y is 'to the left'
# - Z is # 'up' (pointing to the sky)
# - Y is chosen to have right-handed system....
################################################################################

#~ class VectorCoil(CurrentSupply):
class VectorCoil(AnalogOutput):
    """ Vectorcoil is a device to control a coil which creates a field a the
    sample position.

    Basically it is a powersupply device, working in Amps and having two
    additional parameters for calibration the vectorfield, for which these coil
    devices are used.
    """
    parameters = {
        'orientation' : Param('Field vector which is created by this coil in '
                              'mT (measured value!)',
                              settable=True, default=(1., 1., 1.),
                              type=tupleof(float, float, float), unit='mT',
                              category='general',
                             ),
        'calibrationcurrent' : Param('Current in A which created the field '
                                     'given as Parameter orientation.',
                                     settable=True, default=1., type=float,
                                     unit='A',
                                     category='general',
                                    ),
    }


class AlphaStorage(VirtualMotor):
    """ Storage for the spectrometers \\alpha value """
    parameter_overrides = {
        'speed' :       Override(default=0.),
    }

    _callback = None

    def doStart(self, pos):
        VirtualMotor.doStart(self, pos)
        if self._callback is not None:
            try:
                self._callback() #pylint: disable=E1102
            except Exception, e:
                self.log.error('Calling callback failed, %r' % e, exc=1)


class GuideField(MappedMoveable):
    """ Guidefield object.
    needs to be switched to (re-)calculated the required currents for the coils
    calibration is done with a matrix giving the field components created with
    a given current needs the alpha-virtualmotor for calculations
    """
    attached_devices = {
        'alpha' : (AlphaStorage, 'Device which provides the current \alpha'),
        'coils' : ([VectorCoil], 'List of 3 devices used for the vector field'),
    }
    parameter_overrides = {
        'mapping'   : Override(mandatory=False, type=dict,
                               default={'off'   : None,
                                        'perp'  : ( 1., 0., 0.),
                                        '-perp' : (-1., 0., 0.),
                                        'par'   : ( 0., 1., 0.),
                                        '-par'  : ( 0.,-1., 0.),
                                        'z'     : ( 0., 0., 1.),
                                        '-z'    : ( 0., 0.,-1.),
                                        'up'    : ( 0., 0., 1.),
                                        'down'  : ( 0., 0.,-1.),
                                        '0'     : ( 0., 0., 0.),
                                       }),
        'blockingmove' : Override(default=False),
        'precision' : Override(mandatory=False),
    }
    parameters = {
        'background' : Param('Static magnetic field which is always present and'
                             ' should be corrected.',
                             type=tupleof(float,float,float), unit='mT',
                             settable='True', default=(0., 0., 0.),
                             category='general',
                            ),
        'field'         : Param('absolute value of the desired field at the '
                                'sample position.',
                                type=floatrange(0.1, 100), unit='mT',
                                settable='True', default=25.,
                                category='general',
                               ),
    }

    _currentmatrix = None
    _currentmatrix_inv = None
    @lazy_property
    def coils(self):
        return self._adevs['coils']

    @lazy_property
    def alpha(self):
        return self._adevs['alpha']

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)
        M = np.zeros([3,3])
        for i in range(3):
            for j in range(3):
                M[i, j] = (self.coils[j].orientation[i] / \
                           self.coils[j].calibrationcurrent)
        self._currentmatrix = M
        self._currentmatrix_inv = np.linalg.inv(M)
        self.alpha._callback = self._alphaCallBack

    def doShutdown(self):
        self.alpha._callback = None

    def _alphaCallBack(self):
        if self.target and self.target in self.mapping:
            self.doStart(self.target)

    def _startRaw(self, orient):
        if orient:
            orient = np.array(orient)
            # set requested field (may try to compensate background)
            self._setfield(self.field * orient)
        else:	# switch off completely
            self.coils[0].doStart(0.0)
            self.coils[1].doStart(0.0)
            self.coils[2].doStart(0.0)

    #no _readRaw, as self.target is the unmapped (Higher level) value
    def doRead(self, maxage=0):
        return self.target

    def _B2I(self, B=np.array([0.0, 0.0, 0.0])):
        """rotate the requested field around z-axis by beta first we get alpha
        from the spectrometer alpha is the angle between X-axis and \vec{Q} and
        is in degrees
        """
        # read alpha, calculate beta
        alpha = self.alpha.read(0)
        beta = np.radians(90 - alpha)
        R = np.array([
            [np.cos(beta), -np.sin(beta), 0.0],
            [np.sin(beta),  np.cos(beta), 0.0],
            [0.0, 0.0, 1.0]])
        temp = np.dot(self._currentmatrix_inv, np.dot(R, B))
        return temp

    def _I2B(self, I=np.array([0.0, 0.0, 0.0])):
        """calculate field from currents and rotate field around z-axis by -beta
        """
        # read alpha, calculate beta
        alpha = self.alpha.read(0)
        beta = np.radians(90 - alpha)
        RR = np.array([
            [np.cos(beta), -np.sin(beta), 0.0],
            [np.sin(beta),  np.cos(beta), 0.0],
            [0.0, 0.0, 1.0]])
        return np.dot(RR, np.dot(self._currentmatrix, I))

    def _setfield(self, B=np.array([0,0,0])):
        r"""set the given field and returns the actual field (computed from the
        actual currents)
        field components are:
        * Bqperp: component perpendicular to q, but within the scattering plane
        * Bqpar:  component parallel to q (within scattering plane)
        * Bz:     component perpendicular to the scattering plane
        (if TwoTheta==0 & \hbar\omega=0 then this coordinate-system is the same
        as the XYZ of the coils)
        """
        # subtract offset (The field, which is already there, doesn't need to be
        # generated....)
        B = B - np.array(self.background)
        F = self._B2I(B) # compute currents for requested field

        # now check limits
        valueOk = True
        for i, d in enumerate(self.coils):
            check = d.isAllowed(F[i])
            if check[0] == False:
                self.log.error('Can\'t set %r to %s: %s' % \
                               (d, d.format(F[i], unit=True), check[1]), exc=1)
                valueOk = False

        if valueOk == False:
            raise LimitError(check[1])

        # go there
        for i, d in enumerate(self.coils):
            d.start(F[i])

        if self.blockingmove == False:
            return

        # wait to get there
        for d in self.coils:
            d.wait()

        # read back value
        for i, d in enumerate(self.coils):
            F[i] = d.read()

        # now revers the process, calculate the field from the currents and
        # return it
        return self._I2B(F) + np.array(self.background)


class Flipper(MappedMoveable):
    """ class to set the currents of an Spinflipper
    to either 'on' or 'off'
    """
    attached_devices = {
        'field'   : (Moveable, 'CurrentSupply for the Flipping current'),
        'compensate' : (Moveable, 'CurrentSupply for the compensation field'),
        'wavevector' : (Moveable, 'Device reading current k, needed for '
                                  'calculation of flipping current.'),
    }
    parameters = {
        'compcurrent' : Param('Current in A for the compensation coils, if active',
                              settable=True, type=float, unit='A',
                             ),
        'flipcurrent' : Param('polynomial in wavevector to calculate the '
                              'correct flipping current.',
                              settable=True, type=nonemptylistof(float),
                              unit='A', # actually A * Angstroms ** index
                             ),
    }
    parameter_overrides = {
        'mapping' : Override(settable=False, mandatory=False, userparam=False,
                             default=dict(off=0, on=1),
                            ),
        'precision' : Override(mandatory=False),
    }

    @lazy_property
    def field(self):
        return self._adevs['field']

    @lazy_property
    def compensate(self):
        return self._adevs['compensate']

    @lazy_property
    def wavevector(self):
        return self._adevs['wavevector']

    def doStart(self, target):
        if self.mapping.get(target, target) == 0:
            self.field.start(0.)
            self.compensate.start(0)
        elif self.mapping.get(target, target) == 1:
            k = self.wavevector.read(0)
            self.field.start(
                sum(v * (k ** i) for i, v in enumerate(self.flipcurrent)))
            self.compensate.start(self.compcurrent)
        else:
            raise InvalidValueError(self, '%r is an invalid value for this '
                                          'device!' % target)

    def doStop(self):
        # don't stop wavevector!
        multiStop((self.field, self.compensate))

    def doRead(self, maxage=0):
        if self.target:
            return self.target
        return self._inverse_mapping.get(0)

    def doStatus(self, maxage=0):
        return multiStatus((('field', self.field),
                             ('compensate', self.compensate)), maxage)
