#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Bertrand Roessli
#   Marc Janoschek
#   Florian Bernlochner
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
Resolution calculation using the Popovici method.  Based on
neutrons.instruments.tas.tasres from the neutrons Python package, compiled by
Marc Janoschek.
"""

import os
import time

from numpy import pi, radians, degrees, sin, cos, tan, arcsin, arccos, \
     arctan2, abs, sqrt, real, matrix, diag, cross, dot, array, arange, \
     zeros, concatenate, reshape, delete, ceil, floor
from numpy.linalg import inv, det, eig, norm


class unitcell(object):
    """
    Class which models a crystallographic unit cell from given lattice
    parameters and angles.  Further it provides functions to make basic
    calculations with the lattice vectors in the crystallographic and in the
    standard cartesian coordinate system.
    """

    def __init__(self, a, b, c, alpha, beta, gamma):
        """
        Instantiates the class object: necessary input parameters are the
        lattice constants a,b,c in Angstrom and the angles between the
        crystallographic axes, namely alpha, beta, gamma in degrees.
        """

        # unit cell parameters
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.alpha = radians(alpha)
        self.beta  = radians(beta)
        self.gamma = radians(gamma)

        # often used values
        cosa = cos(self.alpha)
        cosb = cos(self.beta)
        cosg = cos(self.gamma)
        sing = sin(self.gamma)

        # conversion matrices
        # (s. International Tables of Crystallography, Volume B, 2nd Edition, p. 360)

        # phi is a needed constant
        phi = sqrt(1 - cosa**2 - cosb**2 - cosg**2 + 2*cosa*cosb*cosg)

        # from crystallographic (x) to cartesian setting (X) with first component
        # parallel to a and third to c* (reciprocal axis)
        # X = Mx, (x in fractional units=>dimensionless, X in dimension of length)
        self.crys2cartMat = matrix(
            [[a, b * cosg, c * cosb],
             [0, b * sing, c * (cosa - cosb*cosg)/sing],
             [0, 0,        c * phi/sing]]
        )

        # from cartesian (X) to crystallographic setting (x) with first
        # component parallel to a and third to c* (reciprocal axis)
        # x = M^(-1)X, (x in fractional units=>dimensionless, X in dimension of length)
        self.cart2crysMat = matrix(
            [[1./a, -1./(a*tan(self.gamma)), (cosa*cosg-cosb)/(a*phi*sing)],
             [0,    1/(b*sing),              (cosb*cosg-cosa)/(b*phi*sing)],
             [0,    0,                       sing/(c*phi)]]
        )

        #----- Real space lattice vectors

        self.a_vec = self.crys2cart(1, 0, 0).transpose()
        self.b_vec = self.crys2cart(0, 1, 0).transpose()
        self.c_vec = self.crys2cart(0, 0, 1).transpose()

        # this is needed if you only want to roatate from the cartesion to the
        # crystal system without changing the length
        self.crys2cartUnit = concatenate((self.a_vec/norm(self.a_vec),
                                          self.b_vec/norm(self.b_vec),
                                          self.c_vec/norm(self.c_vec)))
        self.cart2crysUnit = self.crys2cartUnit.I

        # Volume of unit cell
        self.V = dot(array(self.a_vec)[0],
                     cross(array(self.b_vec)[0], array(self.c_vec)[0]))

        #----- Reciprocal space lattice basis vectors
        self.a_star_vec = 2*pi*cross(array(self.b_vec)[0], array(self.c_vec)[0])/self.V
        self.b_star_vec = 2*pi*cross(array(self.c_vec)[0], array(self.a_vec)[0])/self.V
        self.c_star_vec = 2*pi*cross(array(self.a_vec)[0], array(self.b_vec)[0])/self.V

        #----- Reciprocal lattice index (r.l.u.) to cartesian matrix
        self.rlu2cartMat = concatenate((matrix(self.a_star_vec).T,
                                        matrix(self.b_star_vec).T,
                                        matrix(self.c_star_vec).T), 1)
        self.cart2rluMat = inv(self.rlu2cartMat)

        #----- Reciprocal lattice constants; note that there is a factor
        # 2*pi difference to CrysFML definition
        self.a_star = sqrt(dot(self.a_star_vec, self.a_star_vec))
        self.b_star = sqrt(dot(self.b_star_vec, self.b_star_vec))
        self.c_star = sqrt(dot(self.c_star_vec, self.c_star_vec))

        #----- Reciprocal lattice angles
        self.ralpha = arccos(dot(self.b_star_vec, self.c_star_vec)/(self.b_star*self.c_star))
        self.rbeta = arccos(dot(self.a_star_vec, self.c_star_vec)/(self.a_star*self.c_star))
        self.rgamma = arccos(dot(self.b_star_vec, self.a_star_vec)/(self.b_star*self.a_star))

        #----- Reciprocal cell volume
        self.VR = dot(self.a_star_vec, cross(self.b_star_vec, self.c_star_vec))

        #----- Review this array, I think it has to be transposed to be useful
        self.Q2c = matrix([self.a_star_vec, self.b_star_vec, self.c_star_vec])

        #----- Metric tensors
        self.GD = zeros([3,3])
        self.GR = zeros([3,3])

        # real space
        self.GD[0,0] = self.a**2
        self.GD[1,1] = self.b**2
        self.GD[2,2] = self.c**2

        self.GD[0,1] = self.a * self.b * cos(self.gamma)
        self.GD[0,2] = self.a * self.c * cos(self.beta)
        self.GD[1,2] = self.b * self.c * cos(self.alpha)

        self.GD[1,0] = self.GD[0,1]
        self.GD[2,0] = self.GD[0,2]
        self.GD[2,1] = self.GD[1,2]

        self.GD = matrix(self.GD)

        # reciprocal space
        self.GR[0,0] = self.a_star**2
        self.GR[1,1] = self.b_star**2
        self.GR[2,2] = self.c_star**2

        self.GR[0,1] = self.a_star * self.b_star * cos(self.rgamma)
        self.GR[0,2] = self.a_star * self.c_star * cos(self.rbeta)
        self.GR[1,2] = self.b_star * self.c_star * cos(self.ralpha)

        self.GR[1,0] = self.GR[0,1]
        self.GR[2,0] = self.GR[0,2]
        self.GR[2,1] = self.GR[1,2]

        self.GR = matrix(self.GR)

    def __str__(self):
        """Generates string for output on console or file with information about
        unitcell.
        """
        repstr = "<Unit cell object>\n"
        repstr += "a      b      c      alpha   beta   gamma\n"
        degree_sym = "deg"
        repstr += "%2.3fA %2.3fA %2.3fA %3.1f%s   %3.1f%s   %3.1f%s\n" % \
            (self.a, self.b, self.c, degrees(self.alpha), degree_sym,
             degrees(self.beta), degree_sym, degrees(self.gamma), degree_sym)
        repstr += "a*     b*     c*     alpha*  beta*  gamma*\n"
        repstr += "%2.3fA-1 %2.3fA-1 %2.3fA-1 %3.1f%s   %3.1f%s   %3.1f%s\n" % \
            (self.a_star, self.b_star, self.c_star, degrees(self.ralpha), degree_sym,
             degrees(self.rbeta), degree_sym, degrees(self.rgamma), degree_sym)
        return repstr

    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, unitcell):
            return False
        return self.a == other.a and \
            self.b == other.b and \
            self.c == other.c and \
            self.alpha == other.alpha and \
            self.beta == other.beta and \
            self.gamma == other.gamma

    def crys2cart(self, rx, ry, rz):
        """Calculates vectors in the cartesian coordinate frame in units of
        Angstrom from given (rx,ry,rz) in fractional units in the
        crystallographic frame.
        """
        x = matrix([[float(rx)],[float(ry)],[float(rz)]])
        return self.crys2cartMat * x

    def cart2crys(self, rx, ry, rz):
        """Calculates vectors in the crystallographic frame in fractional units
        from given (rx,ry,rz) in the cartesian frame in units of Angstrom.
        """
        X = matrix([[float(rx)], [float(ry)], [float(rz)]])
        return self.cart2crysMat * X

    def QCart(self, h, k, l):
        """Calculates Q vector in reciprocal space lattice vector."""
        return h*self.a_star_vec + k*self.b_star_vec + l*self.c_star_vec

    def QCartMag(self, h, k, l):
        """Calculates magnitude of the Q vector in units of Angstrom if one
        provides it in hkl [r.l.u.].
        """
        return norm(self.QCart(h, k, l))

    def calctheta(self, h, k, l, lam):
        """Calculates theta angle (in degrees) of Bragg reflection from lattice
        constants and given h, k, l and lambda (in Angstrom).
        """
        Q = self.QCartMag(h,k,l)
        return degrees(arcsin(Q*lam/4/pi))


dummy_config = """\
   1.000    % =0 for circular source, =1 for rectangular source
  13.500    % width/diameter of the source (cm)
   9.000    % height/diameter of the source (cm)
   0.000    % =0 No Guide, =1 for Guide
   7.900    % horizontal guide divergence (minutes/Angs)
  10.000    % vertical guide divergence (minutes/Angs) ???
   1.000    % =0 for cylindrical sample, =1 for cuboid sample
   0.500    % sample width/diameter perp. to Q (cm)
   0.500    % sample width/diameter along Q (cm)
   0.500    % sample height (cm)
   1.000    % =0 for circular detector, =1 for rectangular detector
   2.500    % width/diameter of the detector (cm)
  10.000    % height/diameter of the detector (cm)
   0.200    % thickness of monochromator (cm)
  23.100    % width of monochromator (cm)
  19.800    % height of monochromator (cm)
   0.200    % thickness of analyser (cm)
  17.000    % width of analyser (cm)
  15.000    % height of analyser (cm)
 780.000    % distance between source and monochromator (cm)
 210.000    % distance between monochromator and sample (cm)
  94.000    % distance between sample and analyser (cm)
  94.000    % distance between analyser and detector (cm)
   1.392    % horizontal curvature of monochromator 1/radius (cm-1)
   0.163    % vertical curvature of monochromator (cm-1)
   1.710    % horizontal curvature of analyser (cm-1)
   0.563    % vertical curvature of analyser (cm-1)
 100.000    % distance monochromator-monitor
   4.000    % width monitor
  10.000    % height monitor
"""

dummy_par = """\
   3.355    %DM
   3.355    %DA
  25.000    %ETAM
  25.000    %ETAA
  30.000    %ETAS
   1.000    %SM
  -1.000    %SS
   1.000    %SA
   1.570    %K \AA-1
   2.0      %KFIX ?
 600.000    %ALPHA1
 600.000    %ALPHA2
 600.000    %ALPHA3
 600.000    %ALPHA4
 600.000    %BETA1
 600.000    %BETA2
 600.000    %BETA3
 600.000    %BETA4
  6.2832    %AS
  6.2832    %BS
  6.2832    %CS
  90.000    %AA
  90.000    %BB
  90.000    %CC
   1.000    %AX
   0.000    %AY
   0.000    %AZ
   0.000    %BX
   1.000    %BY
   0.000    %BZ
   0.000    %QX
   0.000    %QY
   0.000    %QZ
   0.000    %EN
   0.000    %dqx (step of scan in qx to calculate phonon width)
   0.000    %dqy (  "             qy  ...)
   0.000    %dqz (  "             qz  ...)
  -0.020    %de  (  "             en  ...)
  40.000    %gh  (gradient) ?
  40.000    %gk ?
   0.000    %gl ?
   1.000    %gmod (slope meV/A-1) ?
"""


class resmat(object):
    """Class which calculates the resolution matrix, and the renormalisation
    volume R0 for a given triple axis parameter set which describes a specific
    setup at a specific instrument by using the Popovici method (REF).

    Based on these two properties several others can be calculated.

    This code was ported from Bertrand Roessli's octave version of the ILL
    rescal MATLAB tools.
    """

    def __init__(self, **par):
        # experimental setup
        self.par = {}
        pars = dummy_par.splitlines()
        for line in pars:
            parts = line.split()
            self.par[parts[1][1:].lower()] = float(parts[0])
        self.par.update(par)
        # instrument definition (lengths and so on defining a specific instrument)
        self.cfg = []
        lines = dummy_config.splitlines()
        for line in lines:
            self.cfg.append(float(line.split()[0]))

        # instrumental setup description
        self.cfgnames = [
            "=0 for circular source, =1 for rectangular source",
            "width/diameter of the source (cm)",
            "height/diameter of the source (cm)",
            "=0 No Guide, =1 for Guide",
            "horizontal guide divergence (minutes/Angs)",
            "vertical guide divergence (minutes/Angs)",
            "=0 for cylindrical sample, =1 for cuboid sample",
            "sample width/diameter perp. to Q (cm)",
            "sample width/diameter along Q (cm)",
            "sample height (cm)",
            "=0 for circular detector, =1 for rectangular detector",
            "width/diameter of the detector (cm)",
            "height/diameter of the detector (cm)",
            "thickness of monochromator (cm)",
            "width of monochromator (cm)",
            "height of monochromator (cm)",
            "thickness of analyser (cm)",
            "width of analyser (cm)",
            "height of analyser (cm)",
            "distance between source and monochromator (cm)",
            "distance between monochromator and sample (cm)",
            "distance between sample and analyser (cm)",
            "distance between analyser and detector (cm)",
            "horizontal curvature of monochromator 1/radius (cm-1)",
            "vertical curvature of monochromator (cm-1)",
            "horizontal curvature of analyser (cm-1)",
            "vertical curvature of analyser (cm-1)",
            "distance monochromator-monitor",
            "width monitor",
            "height monitor"
        ]

        # conversion factors and so on
        # energy pre-multiplier-f*w
        # where f=0.48 for meV to ang-2 - and q0 which is the wavevector
        # transfer in ang-1, are passed over.
        self.f = 0.4826
        self.mon_flag = 1

        # ERROR
        self.ERROR = 0 #is 0 if calculations are fine and 1 if there was a problem
        self.ERRORMSG = ''

        # magnitude of scattering vector
        #----- calculate q0
        #-----input a, b, c; alpha, beta, gamma; qx, qy, qz
        self.unitc = unitcell(self.par['as'],
                              self.par['bs'],
                              self.par['cs'],
                              self.par['aa'],
                              self.par['bb'],
                              self.par['cc'])
        self.q0 = self.unitc.QCartMag(self.par['qx'], self.par['qy'], self.par['qz'])
        self.Q2c = self.unitc.Q2c

        # resolution
        self.R0 = 0
        self.N = matrix(zeros((4,4)))
        # calculate resolution matrix
        self.calc_popovici()
        self.calc_STrafo()

    def calc_popovici(self):
        """Performs the actual calculation."""
        # reset errors before new calculation
        self.ERROR = 0
        self.ERRORMESSAGE = ''

        #----- recalculate q0
        #-----input a, b, c; alpha, beta, gamma; qx, qy, qz
        self.q0 = self.unitc.QCartMag(self.par['qx'], self.par['qy'], self.par['qz'])

        #----- INPUT SPECTROMETER PARAMETERS.
        q0 = self.q0
        f = self.f
        pit = 0.0002908882   # This is a conversion from minutes of arc to radians.

        dm = self.par['dm']            # monochromator d-spacing in Angs.
        da = self.par['da']            # analyser d-spacing in Angs.
        etam = self.par['etam']*pit    # monochromator mosaic [converted from mins->rads]
        etamp = etam                   # vertical mosaic of the monochromator.
        etaa = self.par['etaa']*pit    # analyser mosaic.
        etaap = etaa                   # vertical mosaic spread of the analyser.
        etas = self.par['etas']*pit    # sample mosaic.
        etasp = etas                   # vertical mosaic spread of the sample.
        sm = self.par['sm']            # scattering sense of monochromator [left = +1,right = -1]
        ss = self.par['ss']            # scattering sense of sample [left = +1,right = -1]
        sa = self.par['sa']            # scattering sense of analyser [left = +1,right = -1]
        kfix = self.par['k']           # fixed momentum component in ang-1.
        fx = self.par['kfix']          # fx = 1 for fixed incident and 2 for scattered wavevector.
        alf0 = self.par['alpha1']*pit  # horizontal pre-monochromator collimation.
        alf1 = self.par['alpha2']*pit  # horizontal pre-sample collimation.
        alf2 = self.par['alpha3']*pit  # horizontal post-sample collimation.
        alf3 = self.par['alpha4']*pit  # horizontal post-analyser collimation.
        bet0 = self.par['beta1']*pit   # vertical pre-monochromator collimation.
        bet1 = self.par['beta2']*pit   # vertical pre-sample collimation.
        bet2 = self.par['beta3']*pit   # vertical post-sample collimation.
        bet3 = self.par['beta4']*pit   # vertical post-analyser collimation.
        w = self.par['en']             # energy transfer.

        # _____________________Instrument Parameters________________________________________

        nsou = self.cfg[0]                # =0 for circular source, =1 for rectangular source.
        ysrc = self.cfg[1]                # width/diameter of the source [cm].
        zsrc = self.cfg[2]                # height/diameter of the source [cm].

        flag_guide = self.cfg[3]          # =0 for no guide, =1 for guide.
        guide_h = self.cfg[4]             # horizontal guide divergence [mins/Angs]
        guide_v = self.cfg[5]             # vertical guide divergence [mins/Angs]

        nsam = self.cfg[6]                # =0 for cylindrical sample, =1 for cuboid sample.
        xsam = self.cfg[7]                # sample width/diameter perp. to Q [cm].
        ysam = self.cfg[8]                # sample width/diameter along Q [cm].
        zsam = self.cfg[9]                # sample height [cm].

        ndet = self.cfg[10]               # =0 for circular detector, =1 for rectangular detector.
        ydet = self.cfg[11]               # width/diameter of the detector [cm].
        zdet = self.cfg[12]               # height/diameter of the detector [cm].

        xmon = self.cfg[13]               # thickness of monochromator [cm].
        ymon = self.cfg[14]               # width of monochromator [cm].
        zmon = self.cfg[15]               # height of monochromator [cm].


        xana = self.cfg[16]               # thickness of analyser [cm].
        yana = self.cfg[17]               # width of analyser [cm].
        zana = self.cfg[18]               # height of analyser [cm].

        L0 = self.cfg[19]                 # distance between source and monochromator [cm].
        L1 = self.cfg[20]                 # distance between monochromator and sample [cm].
        L2 = self.cfg[21]                 # distance between sample and analyser [cm].
        L3 = self.cfg[22]                 # distance between analyser and detector [cm].

        romh = sm*self.cfg[23]            # horizontal curvature of monochromator 1/radius [cm-1].
        romv = sm*self.cfg[24]            # vertical curvature of monochromator [cm-1].
        roah = sa*self.cfg[25]            # horizontal curvature of analyser [cm-1].
        roav = sa*self.cfg[26]            # vertical curvature of analyser [cm-1].

        L1mon = self.cfg[27]              #distance monochromator monitor [cm]
        monitorw = self.cfg[28]/sqrt(12)  #monitor width [cm]
        monitorh = self.cfg[29]/sqrt(12)  #monitor height [cm]

        f16 = 1/16.
        f12 = 1/12.

        # _____________________________________________________________________________

        # In addition the parameters f, energy pre-multiplier-f*w
        # where f=0.48 for meV to ang-2 - and q0 which is the wavevector
        # transfer in ang-1, are passed over.

        # Calculate ki and kf, thetam and thetaa
        ki = abs(sqrt(kfix**2+(fx-1)*f*w))  # kinematical equations.
        kf = abs(sqrt(kfix**2-(2-fx)*f*w))

        # Test if scattering triangle is closed

        cos_2theta = (ki**2+kf**2-q0**2)/(2*ki*kf)
        #print cos_2theta
        if (cos_2theta > 1 or cos_2theta < -1):
            self.ERROR = 1
            self.ERRORMESSAGE = 'Scattering Triangle does not close'
            return

        thetaa = sa*arcsin(pi/(da*kf))      # theta angles for analyser
        thetam = sm*arcsin(pi/(dm*ki))      # and monochromator.
        thetas = ss*0.5*arccos((ki**2+kf**2-q0**2)/(2*ki*kf)) # scattering angle from sample.
        phi = arctan2(-kf*sin(2*thetas),ki-kf*cos(2*thetas))

        # Make up the matrices in appendix 1 of M. Popovici (1975).

        # First check for incident guide

        if flag_guide == 1:
            alf0_guide = pit*2*pi*guide_h/ki
            bet0 = pit*2*pi*guide_v/ki

            if alf0_guide <= alf0:
                alf0 = alf0_guide  #take into account collimator in the guide


        G = matrix(zeros((8,8)))
        G[0,0] = 1/alf0**2    # horizontal and vertical collimation matrix. The 4 Soller collimators
        G[1,1] = 1/alf1**2    # are described by a 8x8 diagonal matrix with non-zero elements.
        G[2,2] = 1/bet0**2    # alfi and beti are the FWHM horizontal and vertical beam divergences in
        G[3,3] = 1/bet1**2    # the collimators
        G[4,4] = 1/alf2**2
        G[5,5] = 1/alf3**2
        G[6,6] = 1/bet2**2
        G[7,7] = 1/bet3**2

        F = matrix(zeros((4,4)))
        F[0,0] = 1/etam**2    # monochromator and analyser mosaic matrix. horizontal and vertical mosaic
        F[1,1] = 1/etamp**2    # spreads for monochromator and analyzer crystals
        F[2,2] = 1/etaa**2
        F[3,3] = 1/etaap**2

        C = matrix(zeros((4,8)))
        C[0,0] = 1./2
        C[0,1] = C[0,0]
        C[2,4] = C[0,0]
        C[2,5] = C[0,0]
        C[1,2] = 1/(2*sin(thetam))    # thetam = scattering angle of monochromator
        C[1,3] = -C[1,2]              # thetam = -arcsin(Tm/2ki))epsilonm; Tm(Ta) = 2Pi/dm(da) mono and ana scattering vectors
        C[3,6] = 1/(2*sin(thetaa))    # thetaa = scattering angle of analyzer
        C[3,7] = -C[3,6]              # thetaa = -arcsin(Ta/2kf))epsilona
                                    # epsilonm/a = 1 if sample scattering direction opposite do mono/ana scattering dir, -1 otherwise
        A = matrix(zeros((6,8)))
        A[0,0] = ki/(tan(thetam)*2)
        A[0,1] = -A[0,0]
        A[1,1] = ki
        A[2,3] = A[1,1]
        A[3,4] = kf/(tan(thetaa)*2)
        A[3,5] = -A[3,4]
        A[4,4] = kf
        A[5,6] = A[4,4]

        B = matrix(zeros((4,6)))
        B[0,0] = cos(phi)
        B[0,1] = sin(phi)
        B[0,3] = -cos(phi-2*thetas)    # thetas = scattering angle of
        B[0,4] = -sin(phi-2*thetas)    # 2thetas = arccos[(ki2 + kf2 - Q2)/(2kikf)]
        B[1,0] = -B[0,1]
        B[1,1] = B[0,0]
        B[1,3] = -B[0,4]
        B[1,4] = B[0,3]
        B[2,2] = 1.
        B[2,5] = -1.
        B[3,0] = 2*ki/f
        B[3,3] = -2*kf/f

        # Now include the spatial effects.

        S1I = matrix(zeros((3,3)))
        # --- monochromator spatial covariances ----------
        factor = f12
        S1I[0,0] = factor*xmon**2
        S1I[1,1] = factor*ymon**2
        S1I[2,2] = factor*zmon**2
        S2I = zeros((3,3))
        # --- sample spatial covariances -----------
        if nsam == 0:
            factor = f16
        else:
            factor = f12

        S2I[0,0] = factor*xsam**2
        S2I[1,1] = factor*ysam**2
        S2I[2,2] = f12*zsam**2
        # --- analyser spatial covariances ---------
        factor = f12
        S3I = zeros((3,3))
        S3I[0,0] = factor*xana**2
        S3I[1,1] = factor*yana**2
        S3I[2,2] = factor*zana**2
        # --- construct the full spatial covariance matrix
        SI = zeros((13,13))
        # --- source covariance --------------------
        if nsou == 0:
            factor = f16      # factor for converting diameter**2 to variance**2
        else:
            factor = f12      # factor for converting width**2 to variance**2

        SI[0,0] = factor*ysrc**2
        SI[1,1] = factor*zsrc**2
        # --- add in the mono. sample & analyser ---
        SI[2:5][:,2:5] = S1I
        SI[5:8][:,5:8] = S2I
        SI[8:11][:,8:11] = S3I
        # --- detector covariance ------------------
        if ndet==0:
            factor = f16
        else:
            factor = f12

        SI[11,11] = factor*ydet**2
        SI[12,12] = factor*zdet**2

        S = inv(5.545*SI)

        T = matrix(zeros((4,13)))
        T[0,0] = -1/(2*L0)
        T[0,2] = cos(thetam)*(1/L1-1/L0)/2
        T[0,3] = sin(thetam)*(1/L0+1/L1-2*romh/(sin(thetam)))/2
        T[0,5] = sin(thetas)/(2*L1)
        T[0,6] = cos(thetas)/(2*L1)
        T[1,1] = -1/(2*L0*sin(thetam))
        T[1,4] = (1/L0+1/L1-2*sin(thetam)*romv)/(2*sin(thetam))
        T[1,7] = -1/(2*L1*sin(thetam))
        T[2,5] = sin(thetas)/(2*L2)
        T[2,6] = -cos(thetas)/(2*L2)
        T[2,8] = cos(thetaa)*(1/L3-1/L2)/2
        T[2,9] = sin(thetaa)*(1/L2+1/L3-2*roah/(sin(thetaa)))/2
        T[2,11] = 1/(2*L3)
        T[3,7] = -1/(2*L2*sin(thetaa))
        T[3,10] = (1/L2+1/L3-2*sin(thetaa)*roav)/(2*sin(thetaa))
        T[3,12] = -1/(2*L3*sin(thetaa))

        D = matrix(zeros((8,13)))
        D[0,0] = -1./L0
        D[0,2] = -cos(thetam)/L0
        D[0,3] = sin(thetam)/L0
        D[2,1] = D[0,0]
        D[2,4] = -D[0,0]
        D[1,2] = cos(thetam)/L1
        D[1,3] = sin(thetam)/L1
        D[1,5] = sin(thetas)/L1
        D[1,6] = cos(thetas)/L1
        D[3,4] = -1./L1
        D[3,7] = -D[3,4]
        D[4,5] = sin(thetas)/L2
        D[4,6] = -cos(thetas)/L2
        D[4,8] = -cos(thetaa)/L2
        D[4,9] = sin(thetaa)/L2
        D[6,7] = -1./L2
        D[6,10] = -D[6,7]
        D[5,8] = cos(thetaa)/L3
        D[5,9] = sin(thetaa)/L3
        D[5,11] = 1./L3
        D[7,10] = -D[5,11]
        D[7,12] = D[5,11]

        # Construction of the resolution matrix
        #if det(D*inv(S+T.transpose()*F*T)*D.transpose()) != 0:
        MI = B*A*(inv(inv(D*(inv(S+T.transpose()*F*T))*D.transpose())+G))*A.transpose()*B.transpose() # including spatial effects.
        #else:
        #MI = B*A*(inv(G))*A.transpose()*B.transpose()
        #MI = B*A*[inv[G+C'*F*C]]*A'*B'  # Cooper and Nathans matrix,
        MI[1,1] = MI[1,1]+q0**2*etas**2
        MI[2,2] = MI[2,2]+q0**2*etasp**2
        M = inv(MI)
        NP = 5.545*M                        # Correction factor as input parameters
        N = NP

        #----- Normalisation factor

        #mon = 1          # monochromator reflectivity
        #ana = 1          # detector and analyser crystal efficiency function. [const.]

        self.vi = 0
        self.vf = 0

        #if mon_flag==1
        #   vi = 1
        #else
        #   vi = mon*ki**3*cot[thetam]*15.75*bet0*bet1*etam*alf0*alf1
        #   vi = vi/sqrt[[2*sin[thetam]*etam]**2+bet0**2+bet1**2]
        #   vi = abs[vi/sqrt[alf0**2+alf1**2+4*etam**2]]
        #end
        #
        #vf = ana*kf**3*cot[thetaa]*15.75*bet2*bet3*etaa*alf2*alf3
        #vf = vf/sqrt[[2*sin[thetaa]*etaa]**2+bet2**2+bet3**2]
        #vf = abs[vf/sqrt[alf2**2+alf3**2+4*etaa**2]]
        #
        #R0 = vi*vf*sqrt[det[NP]]/[2*pi]**2  # Dorner form of resolution normalisation
        #                                  # see Mitchell, Cowley and Higgins.

        #Taken from Zheludev's version [RESLIB 3.1]
        #Calculation of prefactor, normalized to source

        Rm = ki**3/tan(thetam)
        Ra = kf**3/tan(thetaa)
        R0 = Rm*Ra*(2*pi)**4/(64*pi**2*sin(thetam)*sin(thetaa))*sqrt(det(F)/det((D*(S+T.transpose()*F*T)**(-1)*D.transpose())**(-1)+G)) #Popovici
        # Werner and Pynn correction
        # for mosaic spread of crystal.
        R0 = abs(R0/(etas*sqrt(1/etas**2+q0**2*N[1,1])))

        #Transform prefactor to Chesser-Axe normalization
        RM_ = matrix(zeros((4,4)))
        RM_[0,0] = M[0,0]
        RM_[1,0] = M[1,0]
        RM_[0,1] = M[0,1]
        RM_[1,1] = M[1,1]
        RM_[0,2] = M[0,3]
        RM_[2,0] = M[3,0]
        RM_[2,2] = M[3,3]
        RM_[2,1] = M[3,1]
        RM_[1,2] = M[1,3]
        RM_[0,3] = M[0,2]
        RM_[3,0] = M[2,0]
        RM_[3,3] = M[2,2]
        RM_[3,1] = M[2,1]
        RM_[1,3] = M[1,2]
        R0 = R0/(2*pi)**2*sqrt(det(RM_))
        #---------------------------------------------------------------------------------------------
        #Include kf/ki part of cross section
        R0 = R0*kf/ki
        #include monitor efficiency
        #Normalisation to flux monitor
        #bshape = matrix(diag((ysrc,zsrc)))
        #mshape = matrix(diag((xmon,ymon,zmon)))
        #monitorshape = matrix(diag((monitorw,monitorh)))
        g = G[0:4][:,0:4]
        f = F[0:2][:,0:2]
        #c = C[0:2][:,0:4]
        t = matrix(zeros((2,7)))
        t[0,0] = -1/(2*L0)  #mistake in paper
        t[0,2] = cos(thetam)*(1/L1mon-1/L0)/2
        t[0,3] = sin(thetam)*(1/L0+1/L1mon-2*romh/(sin(thetam)))/2
        t[0,6] = 1/(2*L1mon)
        t[1,1] = -1/(2*L0*sin(thetam))
        t[1,4] = (1/L0+1/L1mon-2*sin(thetam)*romv)/(2*sin(thetam))
        sinv = matrix(diag((ysrc,zsrc,xmon,ymon,zmon,monitorw,monitorh))) #S-1 matrix
        s = sinv**(-1)
        d = matrix(zeros((4,7)))
        d[0,0] = -1/L0
        d[0,2] = -cos(thetam)/L0
        d[0,3] = sin(thetam)/L0
        d[2,1] = D[0,0]
        d[2,4] = -D[0,0]
        d[1,2] = cos(thetam)/L1mon
        d[1,3] = sin(thetam)/L1mon
        d[1,5] = 0
        d[1,6] = 1/L1mon
        d[3,4] = -1/L1mon
        Rmon = (2*pi)**2/(8*pi*sin(thetam))*sqrt(det(f)/det((d*(s+t.transpose()*f*t)**(-1)*d.transpose())**(-1)+g))
        Rmon = Rmon*ki**3/tan(thetam)
        R0 = R0*ki #1/ki monitor efficiency
        R0 = R0/Rmon
        #------ END OF ZHELUDEV's CORRECTION
        #----- Final error check
        if NP.imag.all() == 0:
            self.ERROR = 0
        else:
            self.ERROR = 1
            self.ERRORMESSAGE = 'Problem with matrix calculation!'
            return

        self.R0 = abs(R0)
        self.NP = NP
        #return (R0, NP, vi, vf, Error)

    def __str__(self):
        """Returns info string about resolution matrix."""
        info = self.par.copy()
        if self.par['kfix'] == 1:
            info['efixstr'] = 'fixed incident energy k_i = %2.4f A-1' % self.par['k']
        else:
            info['efixstr'] = 'fixed final energy k_f = %2.4f A-1' % self.par['k']
        info['q0'] = self.q0
        if not self.ERROR:
            mat = self.NP.tolist()
            info['mat'] = '\n'.join(''.join(('%5.2f' % mat[i][j]).rjust(10)
                                            for j in range(4)) for i in range(4))
            # Calculate Bragg width in direction of scan and for w-scan, and
            # corresponding Lorentz factors
            bragw = self.calcBragg()
            info['brqx'], info['brqy'], info['brqz'], info['brva'], info['brde'] = bragw
            info['R0'] = self.R0

        p1 =  """\
Resolution matrix for a triple axis spectrometer calculated by the Popovici method:

Spectrometer Setup:
===================
d-spacings:   dm = %(dm)1.4f    da = %(da)1.4f
mosaic    : etam = %(etam)1.4f etas = %(etas)1.4f etaa = %(etaa)1.4f
s-sense   :   sm = %(sm)-4i      ss = %(ss)-4i      sa = %(sa)-4i
alpha 1->4:  %(alpha1)i-Mono-%(alpha2)i-Sample-%(alpha3)i-Ana-%(alpha4)i (horizontal collimation)
beta  1->4:  %(beta1)i-Mono-%(beta2)i-Sample-%(beta3)i-Ana-%(beta4)i   (vertical collimation)

Sample Parameters:
==================
Lattice information:
a         b         c         alpha      beta       gamma
%(as)2.3f A   %(bs)2.3f A   %(cs)2.3f A   %(aa)3.1f deg   %(bb)3.1f deg   %(cc)3.1f deg

Scattering plane:
AX      AY      AZ      BX      BY      BZ
%(ax)1.3f   %(ay)1.3f   %(az)1.3f   %(bx)1.3f   %(by)1.3f   %(bz)1.3f

%(efixstr)s
reciprocal space position: qh = %(qx)1.3f qk = %(qy)1.3f ql = %(qz)1.3f (r.l.u.) en = %(en)2.3f (meV)
scattering vector Q = %(q0)2.5f A-1

Resolution Info:
================
""" % info
        if self.ERROR:
            p2 = 'ERROR: ' + self.ERRORMESSAGE
        else:
            p2 = """\
=> Resolution Volume: R0 = %(R0)3.3f A-3*meV

=> Resolution Matrix (in frame Qx, Qy, Qz, E):
%(mat)s

=> Bragg widths:
   Qx       Qy       Qz (A-1)  Vanadium  dE (meV)
   %(brqx)1.5f  %(brqy)1.5f  %(brqz)1.5f   %(brva)1.5f   %(brde)1.5f
""" % info
        return p1 + p2

    __repr__ = __str__

    def calc_STrafo(self):
        """Calculates transformation matrix self.S, which transforms from the
        coordinate frame given in h, k, l (r.l.u.) and E(meV) to cartesian
        crystallographic axis in units of Angstrom^{-1} and meV (Matrix
        self.Q2c; s neutrons.crystal.unitcell modul).

        Then a second transformation into the coordinate frame defined by V1,V2
        and V3 is performed (Matrix U). V1 and V2 are the vector defining the
        scattering plane in the TAS experiments, V3 is perpendicular to the
        scattering plane (zone axis).
        """

        #----- Work out transformations
        a = self
        A1 = matrix([a.par['ax'], a.par['ay'], a.par['az']]).transpose()
        A2 = matrix([a.par['bx'], a.par['by'], a.par['bz']]).transpose()
        V1 = self.Q2c*A1
        V2 = self.Q2c*A2
        #----- Form unit vectors V1, V2, V3 in scattering plane

        V3 = cross(V1.transpose(),V2.transpose())
        V2 = cross(V3,V1.transpose())
        V3 = V3/sqrt(dot(V3,V3.transpose()))
        V2 = V2/sqrt(dot(V2,V2.transpose()))
        V1 = V1.transpose()/sqrt(dot(V1.transpose(),V1))
        V1 = array(V1)[0]
        V2 = array(V2)[0]
        V3 = array(V3)[0].transpose()
        U = matrix([V1, V2, V3])
        self.S = U*self.Q2c

    def sethklen(self, h, k, l, en):
        self.par['qx'] = h
        self.par['qy'] = k
        self.par['qz'] = l
        self.par['en'] = en
        self.calc_popovici()
        self.calc_STrafo()

    def calcSigma(self):
        #calculates sigmas in system h,k,l (r.l.u) en (meV)
        #print self.M
        [E, V] = eig(self.M)

        #print 'Eigenvalues'
        #print E
        #print 'eigenvecs'
        #print V

        E = matrix(real(diag(E)))
        sigma = zeros((1,4))[0]
        sigma[0] = real(1./sqrt(E[0,0]))
        sigma[1] = real(1./sqrt(E[1,1]))
        sigma[2] = real(1./sqrt(E[2,2]))
        sigma[3] = real(1./sqrt(E[3,3]))
        self.b_mat = reshape(inv(V.transpose().transpose()), (1, 16))
        #self.b_mat=reshape(inv((V.transpose())),(1,16))
        #print 'b_mat'
        #print self.b_mat
        return sigma

    def calcResEllipsoid(self, h, k, l, en):
        # set current Q vector and calculate corresponding resolution matrix
        # (sethklen calls self.calc_popovici() to calculate the matrix...
        self.sethklen(h, k, l, en)

        #   [R0,NP,vi,vf,Error]=feval(method,f,Qmag,p,mon_flag);
        self.R0_corrected = real(self.R0/(sqrt(det(self.NP))/(2*pi)**2))
        # corrected resolution volume as Monte Carlo integral is over a
        # normalised ellipsoid.

        # the resolution matrix calculated by self.calc_popovici is in x, y & z
        # coordinate frame defined by
        #   x || Q
        #   z perp to Q outside scattering plane
        #   y completing r.h.s
        # therefore transformation to h,k,l in (r.l.u.) needs to calculated

        # first calculate angle of Q wrt to V1, V2

        # TT is Q vector in system of V1 and V2 that define scattering plane
        TT = real(self.S*matrix([h, k, l]).transpose())
        # cos(theta) and sin(theta) are the projections of the Q vector onto
        # the directions V1 and V2
        cos_theta = TT[0,0]/sqrt(dot(TT.transpose(),TT))
        sin_theta = TT[1,0]/sqrt(dot(TT.transpose(),TT))

        #----- Rotation matrix from system of resolution matrix
        # to system defined by V1, V2, V3 => V1,V2 define scattering plane,
        # V3 is zone axis, thus perpendicular to the scattering plane
        R = [[cos_theta, sin_theta, 0], [-sin_theta, cos_theta, 0], [0, 0, 1]]
        T = matrix(zeros((4, 4)))
        T[3, 3] = 1.
        T[0:3, 0:3] = array(R*self.S).real
        #self.S performs transformation in h,k,l, en ([Rlu] & [meV])
        self.M = T.transpose()*self.NP*T

    def calcBragg(self):
        """resmat function to calculate the widths (FWHM)
        of a Bragg peak from the resolution matrix M.

        Ported from octave/MATLAB

        Output: bragg, Qx, Qy, Qz, Vanadium and DEE widths
        """
        M = matrix(self.NP)

        bragg = [0, 0, 0, 0, 0]
        bragg[0] = 2.3548/sqrt(M[0,0])
        bragg[1] = 2.3548/sqrt(M[1,1])
        bragg[2] = 2.3548/sqrt(M[2,2])
        [r, bragg[3]] = self.calcPhonon(1, matrix([0, 0, 0, 1]))
        bragg[4] = 2.3548/sqrt(M[3,3])
        return abs(bragg)

    def calcPhonon(self,r0,C):
        """resmat  routine to calculate the phonon width of a scan along a
        vector s, and a plane defined by C.X=w. r0 is the resolution constant and
        M is the resolution matrix.

        ported from matlab
        """
        M = matrix(self.NP)
        T = matrix(diag((1, 1, 1, 1)))
        T[3,0:4] = C
        S = inv(T)
        MP = S.transpose()*M*S
        [rp, MP] = rc_int(0, r0, MP)
        [rp, MP] = rc_int(0, rp, MP)
        [rp, MP] = rc_int(0, rp, MP)
        fwhm = 2.35482/sqrt(MP[0,0])
        return [rp, fwhm]

    def showCFG(self):
        """Displays spectrometer configuration."""
        str =  '\nSpectrometer Configuration:\n'
        str += '--------------------------\n\n'
        str += 'NR' + ('Value   :  ').rjust(16) + 'Explanation\n'
        str += '===============================\n'
        for i in range(len(self.cfg)):
            str += '%2i' % i + ('%1.3f   :  ' % self.cfg[i]).rjust(16) + '%s\n' % self.cfgnames[i]
        print str

    def resellipse(self):
        """Returns the projections of the resolution ellipse of a triple axis."""
        A = self.NP

        #----- Remove the vertical component from the matrix.
        B = [[A[0,0], A[0,1], A[0,3]],
             [A[1,0], A[1,1], A[1,3]],
             [A[3,0], A[3,1], A[3,3]]]
        B = matrix(B)
        #----- Work out projections for different cuts through the ellipse

        #----- S is the rotation matrix that diagonalises the projected ellipse

        #----- 1. Qx, Qy plane
        # (this is maximal extension of the resolution ellipsoid parallel to x and
        # y, whereas the slice added later is just a cut through the ellipsoid in
        # the xy-plane)
        R0 = self.R0
        R0P, MP = GaussInt(2, R0, B)
        #print R0P, MP
        hwhm_xp, hwhm_yp, theta = calcEllipseAxis(MP)
        x, y = ellipse_coords(hwhm_xp, hwhm_yp, theta)

        # slice through Qx,Qy plane
        MP = A[0:2,0:2]
        hwhm_xp, hwhm_yp, theta = calcEllipseAxis(MP)
        xslice, yslice = ellipse_coords(hwhm_xp, hwhm_yp, theta)

        #----- 2. Qx, W plane
        R0P, MP = GaussInt(1, R0, B)
        hwhm_xp, hwhm_yp, theta = calcEllipseAxis(MP)
        xxq, yxq = ellipse_coords(hwhm_xp, hwhm_yp, theta)

        # slice through Qx,W plane
        MP = [[A[0,0], A[0,3]], [A[3,0], A[3,3]]]
        hwhm_xp, hwhm_yp, theta = calcEllipseAxis(MP)
        xxqsclice, yxqslice = ellipse_coords(hwhm_xp, hwhm_yp, theta)

        #----- 3. Qy, W plane
        R0P, MP = GaussInt(0, R0, B)
        hwhm_xp, hwhm_yp, theta = calcEllipseAxis(MP)
        xyq, yyq = ellipse_coords(hwhm_xp, hwhm_yp, theta)

        # slice through Qy,W plane
        MP = [[A[1,1], A[1,3]], [A[3,1], A[3,3]]]
        hwhm_xp, hwhm_yp, theta = calcEllipseAxis(MP)
        xyqsclice, yyqslice = ellipse_coords(hwhm_xp, hwhm_yp, theta)

        return x, y, xslice, yslice, xxq, yxq, xxqsclice, yxqslice, xyq, yyq, xyqsclice, yyqslice


def rc_int(index, r0, m):
    """ported from MATLAB

    function that takes a matrix and performs a Gaussian integral
    over the row and column specified by index and returns
    a new matrix. Tested against maple integration.
    """

    r = sqrt(2*pi/m[index,index])*r0

    # remove columns and rows from m
    # that contain the subscript "index".

    mp = m
    b = m[:,index] + m[index,:].transpose()
    c = b[0:len(b)-1]
    c[0:index] = b[0:index]
    c[index:len(b)-1] = b[index+1:len(b)]
    b = c
    T = matrix(zeros((len(mp)-1, len(mp)-1)))
    T[0:index, 0:index] = mp[0:index, 0:index]
    T[index:len(mp)-1, 0:index] = mp[index+1:len(mp), 0:index]
    T[0:index, index:len(mp)-1] = mp[0:index, index+1:len(mp)]
    T[index:(len(mp)-1), index:(len(mp)-1)] = mp[(index+1):len(mp), (index+1):len(mp)]
    #c=[0:len(mp)-1,0:len(mp)-1]
    mp = T
    mp = mp - 1/(4*m[index,index])*b*b.transpose()
    return [r, mp]


# functions for calculating ellipsoid cuts and projections

def calcEllipseAxis(MP):
    const = 1.17741
    MP = matrix(MP)
    theta = 0.5*arctan2(2*MP[0,1], MP[0,0]-MP[1,1])
    S = matrix([[cos(theta), sin(theta)],
                [-sin(theta), cos(theta)]])
    MP = S*MP*S.transpose()
    hwhm_xp = const/sqrt(MP[0,0])
    hwhm_yp = const/sqrt(MP[1,1])
    return hwhm_xp, hwhm_yp, theta

def GaussInt(index, r0, m):
    """Function that takes a matrix and performs a Gaussian integral
    over the row and column specified by index and returns
    a new matrix.

    XXX what is different to rc_int above?
    """
    r = sqrt(2*pi/m[index,index])*r0
    # remove columns and rows from m that contain the subscript "index".
    mp = m
    b = m[:,index]+m[index,:].transpose()
    b = delete(b, index)
    mp = zeros((len(m)-1, len(m)-1))
    mp[0:index, 0:index] = m[0:index, 0:index]
    if index < (len(m)-1):
        mp[index:len(m)-1,0:index] = m[index+1:len(m),0:index]
        mp[0:index,index:len(m)-1] = m[0:index,index+1:len(m)]
        mp[index:len(m)-1,index:len(m)-1] = m[index+1:len(m),index+1:len(m)]
    mp = mp-1./(4*m[index,index])*b.transpose()*b
    return r, mp

def ellipse_coords(a, b, phi):
    """Return coordinates for ellipse with semiaxes a, b and rotated by phi."""
    x0 = 0
    y0 = 0

    th = arange(0, 2*pi+2*pi/100, 2*pi/100)
    x = a*cos(th)
    y = b*sin(th)

    c = cos(phi)
    s = sin(phi)

    th = x*c-y*s+x0
    y = x*s+y*c+y0
    x = th
    return x, y


def pylab_key_handler(event):
    import pylab
    if event.key == 'p':
        # write temporary file in tmp directory of system
        filename = '/tmp/tas%s.ps' % time.strftime('%j%H%M')
        pylab.savefig(filename, dpi=72, facecolor='w', edgecolor='w',
                      orientation='landscape', papertype='a4')
        #self.pylab.close()
        print
        res = os.system('lp %s' % filename)
        if res == 0:
            print 'Successfully sent file %s to the printer!' % filename
        else:
            print 'Error on sending file %s to the printer!' % filename

    elif event.key == 'e':
        # create more or less unique filename
        filename = '/tmp/tas%s.pdf' % time.strftime('%j%H%M')
        pylab.savefig(filename, dpi=72, facecolor='w', edgecolor='w',
                      orientation='landscape', papertype='a4')
        #self.pylab.close()
        print 'Successfully exported file %s!' % filename

    elif event.key == 'q':
        pylab.close()


def plot_ellipsoid(resmat):
    import pylab

    x, y, xslice, yslice, xxq, yxq, xxqslice, yxqslice, xyq, yyq, xyqslice, yyqslice = \
        resmat.resellipse()

    pylab.figure(4)
    pylab.close()

    pylab.ion()
    pylab.figure(4, figsize=(8.5, 6), dpi=120, facecolor='1.0')
    pylab.rc('text', usetex=True)
    pylab.rc('text.latex',
             preamble='\\usepackage{amsmath}\\usepackage{helvet}\\usepackage{sfmath}')
    pylab.subplots_adjust(left=0.11, bottom=0.08, right=0.97, top=0.81,
                          wspace=0.25, hspace=0.27)
    # register event handler to pylab
    pylab.connect('key_press_event', pylab_key_handler)

    pylab.subplot(221)
    pylab.xlabel(r'Q$_x$ (\AA$^{-1}$)')
    pylab.ylabel(r'Q$_y$ (\AA$^{-1}$)')
    pylab.plot(x,y)
    pylab.plot(xslice,yslice)

    ax1 = pylab.gca()
    text  = r"""\noindent\underline{Spectrometer Setup:}\newline
\begin{tabular}{ll}
d-spacings: & $d_M=%(dm)1.4f$\,\AA~~~$d_A=%(da)1.4f$\,\AA \\
mosaic:     & $\eta_M=%(etam)3.1f'$~~~$\eta_S=%(etas)3.1f'$~~~$\eta_A=%(etaa)3.1f'$ \\
s-sense:    & $s_M=%(sm)i$~~~$s_S=%(ss)i$~~~$s_A=%(sa)i$ \\
$\alpha_{1\rightarrow4}$: & %(alpha1)i-Mono-%(alpha2)i-Sample-%(alpha3)i-Ana-%(alpha4)i (hor. coll.) \\
$\beta_{1\rightarrow4}$:  & %(beta1)i-Mono-%(beta2)i-Sample-%(beta3)i-Ana-%(beta4)i   (vert. coll.) \\
\end{tabular}
""" % resmat.par
    t1 = pylab.text(-0.25, 1.57, text.replace('\n', ''),
                    horizontalalignment='left', verticalalignment='top',
                    transform=ax1.transAxes)
    t1.set_size(10)

    pylab.subplot(222)
    pylab.xlabel(r'Q$_x$ (\AA$^{-1}$)')
    pylab.ylabel('Energy (meV)')
    pylab.plot(xxq,yxq)
    pylab.plot(xxqslice,yxqslice)

    ax2 = pylab.gca()
    text  = r"""\noindent\underline{Sample Parameters:}\newline
\begin{tabular}{llllll}
$a$ (\AA) & $b$ (\AA) & $c$ (\AA) & $\alpha$ ($^{\circ}$) & $\beta$ ($^{\circ}$) & $\gamma$ ($^{\circ}$) \\
%(as)2.3f & %(bs)2.3f & %(cs)2.3f & %(aa)3.1f & %(bb)3.1f & %(cc)3.1f \\
\end{tabular}\newline """ % resmat.par
    if resmat.par['kfix'] == 1:
        text += r'fixed incident energy $k_i=%2.4f$\,\AA$^{-1}$ ($\equiv %4.2f$\,meV)\newline ' % \
            (resmat.par['k'], resmat.par['k']**2*2.07)
    else:
        text += r'fixed final energy $k_f=%2.4f$\,\AA$^{-1}$ ($\equiv %4.2f$\,meV)\newline ' % \
            (resmat.par['k'], resmat.par['k']**2*2.07)
    text += r'position: qh = %1.3f qk = %1.3f ql = %1.3f (r.l.u.) en = %2.3f (meV)\newline ' % \
        (resmat.par['qx'], resmat.par['qy'], resmat.par['qz'], resmat.par['en'])
    text += r'modulus of scattering vector $Q = %2.5f$\,\AA$^{-1}$' % resmat.q0
    t2 = pylab.text(-0.25, 1.57, text.replace('\n', ' '),
                    horizontalalignment='left', verticalalignment='top',
                    transform=ax2.transAxes)
    t2.set_size(10)

    pylab.subplot(223)
    pylab.xlabel(r'Q$_y$ (\AA$^{-1}$)')
    pylab.ylabel(r'Energy (meV)')
    pylab.plot(xyq,yyq)
    pylab.plot(xyqslice,yyqslice)

    pylab.subplot(224)
    ax3 = pylab.gca()
    pylab.axis('off')
    pylab.rc('text', usetex=True)
    text  = r'\noindent\underline{\textbf{Resolution Info:}}\newline ' + \
        r'Resolution Volume: $R_0 = %7.5g$ (\AA$^{-3}$\,meV)\newline\newline ' % resmat.R0
    mat = resmat.NP.tolist()
    text += r'Resolution Matrix (in frame $Q_x$, $Q_y$, $Q_z$, $E$):\newline '
    text += (r'$M = \left(\begin{array}{rrrr} %5.2f & %5.2f & %5.2f & %5.2f\\ ' \
             r'%5.2f & %5.2f & %5.2f & %5.2f\\ %5.2f & %5.2f & %5.2f & %5.2f\\ ' \
             r'%5.2f & %5.2f & %5.2f & %5.2f \end{array}\right)$\newline\newline\newline ') \
             % (mat[0][0], mat[0][1], mat[0][2], mat[0][3],
                mat[1][0], mat[1][1], mat[1][2], mat[1][3],
                mat[2][0], mat[2][1], mat[2][2], mat[2][3],
                mat[3][0], mat[3][1], mat[3][2], mat[3][3])
    text += r'Bragg width:\newline '
    text += r'\begin{tabular}{lllll} '
    text += r'$Q_x$ (\AA$^{-1}$) & $Q_y$ (\AA$^{-1}$) & $Q_z$ (\AA$^{-1}$) & Vanadium & dE (meV) \\ '
    bragw = tuple(resmat.calcBragg())
    text += r'%1.5f & %1.5f & %1.5f & %1.5f & %1.5f \\ ' % bragw[:5]
    text += '\end{tabular}'
    t3 = pylab.text(-0.13, 1.0, text,
                    horizontalalignment='left', verticalalignment='top',
                    transform=ax3.transAxes)
    t3.set_size(10)

def plot_scan(resmat, q, dq, np):
    import pylab

    qh = float(q[0])
    qk = float(q[1])
    ql = float(q[2])
    en = float(q[3])
    dqh = float(dq[0])
    dqk = float(dq[1])
    dql = float(dq[2])
    den = float(dq[3])

    #calculate scan
    n = np
    np = float(np)
    h = arange(qh-dqh*floor(np/2), qh+dqh*ceil(np/2), dqh)
    k = arange(qk-dqk*floor(np/2), qk+dqk*ceil(np/2), dqk)
    l = arange(ql-dql*floor(np/2), ql+dql*ceil(np/2), dql)
    e = arange(en-den*floor(np/2), en+den*ceil(np/2), den)

    if dqh == 0.0:
        h = zeros(n)+qh
    if dqk == 0.0:
        k = zeros(n)+qk
    if dql == 0.0:
        l = zeros(n)+ql
    if den == 0.0:
        e = zeros(n)+en

    pylab.figure(4)
    pylab.close()

    pylab.ion()
    pylab.figure(4, figsize=(8.5, 6), dpi=120, facecolor='1.0')
    pylab.rc('text', usetex=True)
    pylab.rc('text.latex',
             preamble='\\usepackage{amsmath}\\usepackage{helvet}\\usepackage{sfmath}')
    pylab.subplots_adjust(left=0.11, bottom=0.08, right=0.97, top=0.96,
                          wspace=0.25, hspace=0.39)
    # register event handler to pylab
    pylab.connect('key_press_event', pylab_key_handler)

    elliplist = []
    errors = []
    #print '\n=> Simulating scan:\n'
    #print 'h    k    l    en'
    #print '-----------------'
    for i in range(n):
        resmat.sethklen(h[i], k[i], l[i], e[i])
        #print self.resmat.ERROR
        if not resmat.ERROR:
            #print '%+1.4f %+1.4f %+1.4f %+1.4f' %  (h[i], k[i], l[i], e[i])
            elliplist.append(resmat.resellipse())
        else:
            print '%+1.4f %+1.4f %+1.4f %+1.4f => scattering triangle did not ' \
                'close for this point => excluded from simulation' %  (h[i], k[i], l[i], e[i])
            errors.append(i)

    # remove points for that scattering triangle did not close
    h = delete(h, errors)
    k = delete(k, errors)
    l = delete(l, errors)
    e = delete(e, errors)

    if den == 0.0: # q-scans plot energies as y axis
        q = 0.0
        if dqh != 0.0:
            q = h
        elif dqk != 0.0:
            q = k
        elif dql != 0.0:
            q = l

        pylab.subplot(311)
        pylab.xlabel(r'$Q_x$ (\AA$^{-1}$)')
        pylab.ylabel(r'$Q_y$ (\AA$^{-1}$)')
        for i in range(len(elliplist)):
            x, y, xslice, yslice = elliplist[i][0:4]
            x += q[i]
            xslice += q[i]

            pylab.plot(x, y, 'b')
            pylab.plot(xslice, yslice, 'g')

        pylab.subplot(312)
        pylab.xlabel(r'$Q_y$ (\AA$^{-1}$)')
        pylab.ylabel(r'Energy (meV)')
        for i in range(len(elliplist)):
            xyq, yyq, xyqslice, yyqslice = elliplist[i][8:12]
            xyq += q[i]
            xyqslice += q[i]

            pylab.plot(xyq, yyq, 'b')
            pylab.plot(xyqslice, yyqslice, 'g')

        pylab.subplot(313)
        pylab.xlabel(r'$Q_x$ (\AA$^{-1}$)')
        pylab.ylabel('Energy (meV)')
        for i in range(len(elliplist)):
            xxq, yxq, xxqslice, yxqslice = elliplist[i][4:8]
            xxq += q[i]
            xxqslice += q[i]
            pylab.plot(xxq, yxq, 'b')
            pylab.plot(xxqslice, yxqslice, 'g')

    else: # energy scans plot energies as x-axis
        pylab.subplot(311)
        pylab.xlabel(r'$Q_x$ (\AA$^{-1}$)/Energy (meV)')
        pylab.ylabel(r'$Q_y$ (\AA$^{-1}$)')
        for i in range(len(elliplist)):
            x, y, xslice, yslice = elliplist[i][0:4]
            x += e[i]
            xslice += e[i]

            pylab.plot(x,y, 'b')
            pylab.plot(xslice,yslice, 'g')

        pylab.subplot(312)
        pylab.ylabel(r'$Q_y$ (\AA$^{-1}$)')
        pylab.xlabel(r'Energy (meV)')
        for i in range(len(elliplist)):
            xyq, yyq, xyqslice, yyqslice = elliplist[i][8:12]
            yyq += e[i]
            yyqslice += e[i]

            pylab.plot(yyq,xyq, 'b')
            pylab.plot(yyqslice,xyqslice, 'g')

        pylab.subplot(313)
        pylab.ylabel(r'$Q_x$ (\AA$^{-1}$)')
        pylab.xlabel('Energy (meV)')
        for i in range(len(elliplist)):
            xxq, yxq, xxqslice, yxqslice = elliplist[i][4:8]
            yxq += e[i]
            yxqslice += e[i]

            pylab.plot(yxq,xxq, 'b')
            pylab.plot(yxqslice,xxqslice, 'g')
