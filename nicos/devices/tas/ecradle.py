#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Peter Link <peter.link@frm2.tum.de>
#   Holger Gibhardt <hgibhar@gwdg.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Eulerian cradle calculations."""

from numpy import array, cross, dot, cos, sin, sqrt, arctan2, zeros, identity
from numpy.linalg import inv, norm

from nicos.core import Moveable, Param, Override, NicosError, vec3, tupleof, \
    ComputationError, usermethod, multiStatus, Attach
from nicos.devices.tas.cell import Cell, D2R


class EulerianCradle(Moveable):
    """
    First (simple) integration of the Eulerian cradle calculations into NICOS.

    This device is moved to a scattering plane, given by two vectors, by moving
    the chi and omega circles of the cradle.  It then sets the sample's
    orientation reflections and psi0 so that the TAS device can move in the
    usual psi-phi scattering plane.

    Angle naming:

    - rotation of the cradle: psi (IT: omega)
    - big circle of the cradle: chi
    - small circle of the cradle: omega (IT: phi)
    - scattering angle: phi (International Tables: two-theta)
    """

    attached_devices = {
        'cell':  Attach('The sample cell object to modify', Cell),
        'tas':   Attach('Triple-axis device (to get scattering sense)', Moveable),
        'chi':   Attach('Eulerian chi axis', Moveable),
        'omega': Attach('Eulerian omega axis (smallest circle)', Moveable),
    }

    parameters = {
        'reflex1': Param('First orientation reflex', type=vec3,
                         category='sample', settable=True),
        'reflex2': Param('Second orientation reflex', type=vec3,
                         category='sample', settable=True),
        'angles1': Param('Angles [psi, chi, om, phi] for first reflex',
                         type=tupleof(float, float, float, float),
                         category='sample', settable=True),
        'angles2': Param('Angles [psi, chi, om, phi] for second reflex',
                         type=tupleof(float, float, float, float),
                         category='sample', settable=True),
    }

    parameter_overrides = {
        'unit':    Override(mandatory=False),
    }

    hardware_access = False

    valuetype = tupleof(vec3, vec3)

    def doRead(self, maxage=0):
        # XXX how to get the real plane?
        return self.target

    def doStart(self, value):
        r1, r2 = value
        for val in self.reflex1, self.reflex2, self.angles1, self.angles2:
            if all(v == 0 for v in val):
                raise NicosError(self,
                    'Please first set the Eulerian cradle orientation '
                    'with the reflex1/2 and angles1/2 parameters')
        sense = self._attached_tas.scatteringsense[1]
        self._omat = self.calc_or(sense)
        ang = self.euler_angles(r1, r2, 2, 2, sense,
                                self._attached_chi.userlimits,
                                self._attached_omega.userlimits)
        psi, chi, om, _phi = ang
        self.log.debug('euler angles: %s' % ang)
        self.log.info('moving %s to %12s, %s to %12s' % (self._attached_chi,
                         self._attached_chi.format(chi, unit=True),
                         self._attached_omega,
                         self._attached_omega.format(om, unit=True)))
        self._attached_chi.move(chi)
        self._attached_omega.move(om)
        self._attached_chi.wait()
        self._attached_omega.wait()
        self._attached_cell.orient1 = r1
        self._attached_cell.orient2 = r2
        wantpsi = self._attached_cell.cal_angles(r1, 0, 'CKF', 2, sense,
            self._attached_tas.axiscoupling, self._attached_tas.psi360)[3]
        self._attached_cell.psi0 += wantpsi - psi

    def doStatus(self, maxage=0):
        return multiStatus(((name, self._adevs[name])
                            for name in ['chi', 'omega']), maxage)

    @usermethod
    def calc_plane(self, r1, r2=None):
        if r2 is None:
            r1, r2 = r1
        for val in self.reflex1, self.reflex2, self.angles1, self.angles2:
            if all(v == 0 for v in val):
                raise NicosError(self,
                    'Please first set the Eulerian cradle orientation '
                    'with the reflex1/2 and angles1/2 parameters')
        sense = self._attached_tas.scatteringsense[1]
        self._omat = self.calc_or(sense)
        ang = self.euler_angles(r1, r2, 2, 2, sense,
                                self._attached_chi.userlimits,
                                self._attached_omega.userlimits)
        self.log.info('found scattering plane')
        self.log.info('%s: %20s' % (self._attached_chi,
                         self._attached_chi.format(ang[1], unit=True)))
        self.log.info('%s: %20s' % (self._attached_omega,
                         self._attached_omega.format(ang[2], unit=True)))

    def euler_angles(self, target_q, another, ki, kf, sense,
                     chilimits=(-180, 180), omlimits=(-180, 180)):
        """Calculates the eulerian angles of *target_q* with the condition
        that the scattering plane is spanned by q and the *another* vector.

        Local variables used by calec from Eckold start with ec_...

        The result is the vector of the euler angles (psi, chi, om, phi) in
        Eckolds notation.
        """
        omat = self._omat
        Bmat = self._Bmat

        # calculate phi from q, ki, kf
        self.log.debug("Bmat = %s" % Bmat)
        ##was: ec_q = dot(Bmat, target_q)
        ec_q = self._attached_cell.hkl2Qcart(*target_q)
        self.log.debug("ec_q = %s" % ec_q)
        phi = self._attached_cell.cal_phi(ec_q, ki, kf, sense)
        self.log.debug("phi = %s" % phi)
        ec_ql = norm(ec_q)
        ec_a = dot(Bmat, another)

        ec_al = norm(ec_a)
        ec_b  = cross(ec_q, ec_a)
        ec_bl = norm(ec_b)
        self.log.debug('vector perp q and sp1 ec_b = %s' % ec_b)
        if ec_bl < 0.01:
            # should be:
            # der Q-Vektor ist parallel zu sp1 (der erste Reflex)
            raise ComputationError('selected Q and second vector are parallel; '
                                   'no scattering plane is defined by them')

        # transform q and a to lab coordinates
        ec_r = dot(omat, ec_q/ec_ql)
        self.log.debug('unit Q vector in lab system ec_r = %s' % ec_r)
        ec_a = dot(omat, ec_a/ec_al)
        self.log.debug('reflection 1 in lab system ec_a = %s' % ec_a)

        # calculate Q1 defined by ki, kf and phi

        ec_q1 = array([ki-kf*cos(phi*D2R), -kf*sin(phi*D2R), 0])
        self.log.debug('scattering vector as function of ki 2: ec_q1 = %s' % ec_q1)
        ec_q1 = ec_q1/ec_ql
        self.log.debug('unit scattering vector: ec_q1 = %s' % ec_q1)

        # calculate the angles
        ec_b = cross(ec_r, ec_a)
        ec_bl = norm(ec_b)
        ec_bl2 = sqrt(ec_b[0]**2 + ec_b[1]**2)
        self.log.debug('B vector as ec_b = %s' % ec_b)

        # now the case selection

        # eckolds case 2 first

        if ec_bl2 < 0.001:  # means b[0]=b[1]=0
            self.log.debug('case 2: b[0] == b[1] == 0')
            ec_chi = 0
            if ec_b[2] >= 0:
                ec_xlchi = 1.0
            else:
                ec_xlchi = -1.0
                ec_chi = 180
            # this is direct what stands in calec
            ec_copom = ec_xlchi*ec_q1[1]*ec_r[1] + ec_q1[0]*ec_r[0]
            ec_sipom = ec_xlchi*ec_q1[1]*ec_r[0] - ec_q1[0]*ec_r[1]
            ec_pom = arctan2(ec_sipom, ec_copom)/D2R

            # acos(ec_copom) should be the same!

            ec_psi = phi/2
            ec_om = ec_pom - ec_psi*ec_xlchi
            if ec_om < -180:
                ec_om += 360
            if ec_om > 180:
                ec_om -= 360
            return array([ec_psi, ec_chi, ec_om, phi])

        #  now the distinction for b [1] >< 0

        if abs(ec_b[0]) < 0.001:   # b[0] = 0
            self.log.debug('case 1: b[0] == 0 and b[1] != 0')
            if ec_b[1] >= 0:
                ec_xlb = 1
            else:
                ec_xlb = -1
            ec_coom = 1
            ec_siom = 0
            ec_cochi = ec_xlb*ec_b[2]/ec_bl
            ec_sichi = ec_xlb*ec_b[1]/ec_bl
            ec_xh = ec_sichi*(ec_r[1]*ec_b[2]/ec_b[1] - ec_r[2])
            ec_xah = ec_r[0]**2 + ec_xh**2
            # in der folgenden Zeile gabe es Fehler:
            # die r[1] muss r[0] heissen
            # ec_copsi1 = ec_q1[0]*ec_r[1]/ec_xah
            ec_copsi1 = ec_q1[0]*ec_r[0]/ec_xah
            ec_copsi2 = ec_xh/ec_xah*ec_q1[1]
            ec_sipsi1 = ec_q1[1]*ec_r[0]/ec_xah
            ec_sipsi2 = -ec_xh/ec_xah*ec_q1[0]
        else:               # b[0] >< 0
            self.log.debug('case 3: b[0] != 0 and b[1] != 0')
            if ec_b[0] >= 0:
                ec_xlb = 1
            else:
                ec_xlb = -1
            ec_a2 = cross(ec_r, ec_b)
            ec_xh = (ec_a2[0]*ec_b[1] - ec_a2[1]*ec_b[0])/ec_bl/ec_bl2
            ec_xa = ec_a2[2]/ec_bl2
            ec_xah = ec_xa*ec_xa+ec_xh*ec_xh
            ec_coom = ec_xlb*ec_b[1]/ec_bl2
            ec_siom = ec_xlb*ec_b[0]/ec_bl2
            ec_cochi = ec_xlb*ec_b[2]/ec_bl
            ec_sichi = ec_bl2/ec_bl
            ec_copsi1 = ec_xlb*ec_xa*ec_q1[0]/ec_xah
            ec_copsi2 = ec_xh*ec_q1[1]/ec_xah
            ec_sipsi1 = ec_xlb*ec_xa*ec_q1[1]/ec_xah
            ec_sipsi2 = -ec_xh*ec_q1[0]/ec_xah

        self.log.debug('cochi  = %s, sichi  = %s' % (ec_cochi, ec_sichi))
        self.log.debug('copsi1 = %s, copsi2 = %s' % (ec_copsi1, ec_copsi2))
        self.log.debug('sipsi1 = %s, sipsi2 = %s' % (ec_sipsi1, ec_sipsi2))

        #
        #   THE SIGNES OF OM AND CHI CAN BE CHOOSEN ARBITRARILY
        #   CALCULATE THE 4 DIFFERENT SETS OF ANGLES CORRESPONDING
        #   TO THE COMBINATIONS OF THESE SIGNES
        #
        #   SELECT THE MOST APPROPRIATE SET OF ANGLES
        #
        #   FIRST CRITERION: SCATTERING VECTOR Q AND REFERENCE VECTOR A1
        #             ARE ORIENTED IN A WAY THAT THE ANGLE BETWEEN
        #             Q AND A1 IS POSITIV
        #
        #   SECOND CRITERION:  CHI MUST BE WITHIN THE ALLOWED RANGE
        #             GIVEN BY SOFT LIMITS
        #   THIRD CRITERION: PSI MUST BE CHOSEN IN SUCH A WAY THAT
        #             NEITHER THE INCIDENT NOR THE SCATTERED
        #             BEAM IS SHADED BY THE LARGE CIRCLE OF THE
        #             EULARIAN CRADLE
        #

        ec_chil, ec_chiu = chilimits
        ec_oml, ec_omu = omlimits
        for ec_xlom in [-1, 1]:   # has been do 8
            for ec_xlchi in [-1, 1]:  # has been do 9
                self.log.debug('xlom, xlchi, xlb, mmm = %s, %s, %s, %s' %
                               (ec_xlom, ec_xlchi, ec_xlb, ec_xlchi*ec_xlom*ec_xlb))
                if ec_xlchi*ec_xlom*ec_xlb < 0:
                    continue   # corresponds to: go to 9
                ec_d1 = ec_xlom*ec_xlchi*ec_cochi
                ec_d2 = ec_xlchi*ec_sichi
                ec_cc = arctan2(ec_d2, ec_d1)/D2R
                self.log.debug('xlom, xlchi, ec_cc = %s, %s, %s' %
                               (ec_xlom, ec_xlchi, ec_cc))
                if ec_cc < -180:
                    ec_cc += 360
                if ec_cc >  180:
                    ec_cc -= 360
                if ec_cc < ec_chil or ec_cc > ec_chiu:
                    continue
                ec_d1 = ec_xlom*ec_copsi1 + ec_xlchi*ec_copsi2
                ec_d2 = ec_xlom*ec_sipsi1 + ec_xlchi*ec_sipsi2
                ec_p = arctan2(ec_d2, ec_d1)/D2R
                self.log.debug('ec_p = %s' % ec_p)
                if ec_p < -180:
                    ec_p += 360.
                if ec_p >  180:
                    ec_p -= 360.
                self.log.debug('ec_p = %s' % ec_p)
    #
    #         treatment of the third criterion
    #
    #
    #   if j=1 the incident beam is considered
    #   if j-2 the scattered beam is considered
    #       attention made ec_aa = 180 or phi directly
    #
    #            for ec_aa in [180,phi]:   #    do 10 jj=1,2
    #                for ec_ii in [-360,0,360]:    # do 11 ii=1,3
    #                    ec_x=ec_p+ec_ii
    #                    if((ec_x>ec_aa+55) and (ec_x<ec_aa+90)):break          # go to 9
    #                    if((ec_x>ec_aa-90) and (ec_x<ec_aa-55)):break                  # go to 9
    #                    if((ec_cc<-160) or (ec_cc>150)):continue               # go to 11
    #                    if(ec_cc>-30):                                         # has been go to 110
    #                         if(ec_cc<20.): continue                            # go to 11
    #                         if((ec_x>ec_aa-135.) and (ec_x<ec_aa-55)):break    # go to 9
    #                         if(ec_cc<30.): continue                            # go to 11
    #                         if((ec_x>ec_aa+35.) and (ec_x<ec_aa+90)):break     # go to 9
    #                         if((ec_x>ec_aa+55) and (ec_x<ec_aa+135.)):break    # go to 9
    #                         if(ec_cc<-150):continue                            # go to 11
    #                         if((ec_x>ec_aa-90) and (ec_x<ec_aa-35)):break      # go to 9
    ##   11     continue
    #                    break
    ##   10   continue
                ec_d1 = ec_xlom*ec_coom
                ec_d2 = ec_xlom*ec_siom
                ec_om = arctan2(ec_d2, ec_d1)/D2R
                self.log.debug('ec_om = %s' % ec_om)
                if ec_om < -180.:
                    ec_om += 360.
                if ec_om > 180.:
                    ec_om -= 360.
                if ec_om < ec_oml or ec_om > ec_omu:
                    continue                 #  go to 9
                return array([ec_p, ec_cc, ec_om, phi])

        raise ComputationError('could not find a Eulerian cradle position for '
                               'q = %s' % (target_q,))

    def calc_rotmat(self, a_vector, an_angle):
        """Calculates the 3x3 matrix for a rotation with angle around
        direction vector
        vector given in x,y,z lab coordinate base
        """
        # v = norm(a_vector)
        v = a_vector
        result = zeros((3, 3))
        a = an_angle*D2R
        co = cos(a)
        si = sin(a)
        result[0,0] = co
        result[1,1] = co
        result[2,2] = co
        result[0,1] = -si*v[2]
        result[0,2] = si*v[1]
        result[1,2] = -si*v[0]
        result[1,0] = -result[0,1]
        result[2,0] = -result[0,2]
        result[2,1] = -result[1,2]
        for i in range(3):
            for j in range(3):
                result[i,j] += (1-co)*v[i]*v[j]
        return result

    def calc_euler(self, psi, chi, om):
        """This is the exact copy of Eckold's SR Euler."""
        temp = zeros((3, 3))   # init 3x3 matrix
        sipsi = sin(psi*D2R)
        copsi = cos(psi*D2R)
        sichi = sin(chi*D2R)
        cochi = cos(chi*D2R)
        siom = sin(om*D2R)
        coom = cos(om*D2R)
        temp[0,0] = copsi*coom - sipsi*cochi*siom
        temp[0,1] = -copsi*siom - sipsi*cochi*coom
        temp[0,2] = sipsi*sichi
        temp[1,0] = sipsi*coom + copsi*cochi*siom
        temp[1,1] = -sipsi*siom + copsi*cochi*coom
        temp[1,2] = -copsi*sichi
        temp[2,0] = sichi*siom
        temp[2,1] = sichi*coom
        temp[2,2] = cochi
        return temp

    def calc_orient(self, h1, h2, r1, r2, mode='3x3'):
        """This is Eckolds SR ORIENT.

        Given h1,r1 h2,r2 four vectors in laboratory coordinates,
        orient calculates the matrix
        transforming h1 in r1 and h2 in r2 simultanously.
        """
        # Normalize all vectors
        h1n = h1 / norm(h1)
        h2n = h2 / norm(h2)
        r1n = r1 / norm(r1)
        r2n = r2 / norm(r2)
        y1 = r1n - h1n
        y2 = r2n - h2n
        # calculate the axis of rotation
        if norm(y1) < 0.001 and norm(y2) < 0.001:
            return identity(3)
        if norm(y1) < 0.001:
            r0 = r1n
        elif norm(y2) < 0.001:
            r0 = r2n
        else:
            r0 = cross(y1, y2)
            if norm(r0) < 0:
                raise ComputationError('error in orient: no solution for Omat')
            r0 = r0 / norm(r0)
        rr1 = dot(r0, r1n)
        rr2 = dot(r0, r2n)
        rh1 = dot(r0, h1n)
        rh2 = dot(r0, h2n)
        r1n = r1n - rr1*r0
        r2n = r2n - rr2*r0
        h1n = h1n - rh1*r0
        h2n = h2n - rh2*r0
        x1 = cross(r1n, h1n)
        x2 = cross(r2n, h2n)
        cos1 = dot(h1n, r1n)
        cos2 = dot(h2n, r2n)
        xx1 = dot(x1, r0)
        xx2 = dot(x2, r0)
        cos1 = cos1 / norm(r1n) / norm(h1n)
        cos2 = cos2 / norm(r2n) / norm(h2n)
        a1 = sqrt(1 - cos1**2)
        a2 = sqrt(1 - cos2**2)
        if xx1 > 0:
            a1 *= -1
        if xx2 > 0:
            a2 *= -1
        alfa1 = arctan2(a1, cos1)/D2R
        #print alfa1
        alfa2 = arctan2(a2, cos2)/D2R
        #print alfa2
        if abs(alfa1 - alfa2) > 0.7:
            raise ComputationError('error in orient: no solution for Omat')
        alfa = (alfa1 + alfa2)/2
        if mode == '3x3':
            return self.calc_rotmat(r0, alfa)
        return [r0[0], r0[1], r0[2], alfa]  # Eckold's notation

    @usermethod
    def calc_or(self, sense=None):
        """Given:
        two reflections hkl1,hkl2 in Miller indices
        two sets of angles psi, chi, om, phi  as ang1 and ang2
        calculates the orientation matrix omat as 3x3 matrix

        needs the scattering sense of the sample axe
        needs the sample's smat matrix
        """
        if sense is None:
            sense = self._attached_tas.scatteringsense[1]
        hkl1 = self.reflex1
        hkl2 = self.reflex2
        ang1 = self.angles1
        ang2 = self.angles2
        cell = self._attached_cell
        self.log.debug('re-setting orientation reflections of cell')
        cell.orient1 = [1, 0, 0]
        cell.orient2 = [0, 1, 0]
        self._Bmat = cell._matrix
        #print 'd1 (psi=%f chi =%f om = %f\n' %(ang1[0],ang1[1],ang1[2]), \
        #      self.calc_euler(ang1[0],ang1[1],ang1[2])
        #print 'd2 (psi=%f chi =%f om = %f\n' %(ang2[0],ang2[1],ang2[2]), \
        #      self.calc_euler(ang2[0],ang2[1],ang2[2])
        d1_inv = inv(self.calc_euler(ang1[0], ang1[1], ang1[2]))
        d2_inv = inv(self.calc_euler(ang2[0], ang2[1], ang2[2]))
        #print 'd1_inv = \n', d1_inv
        #print 'd2_inv = \n', d2_inv
        ec_q1 = [cos((90-ang1[3]/2)*D2R), -sense*sin((90-ang1[3]/2)*D2R), 0]
        ec_q2 = [cos((90-ang2[3]/2)*D2R), -sense*sin((90-ang2[3]/2)*D2R), 0]
        self.log.debug('ec_q1 = %s, ec_q2 = %s' % (ec_q1, ec_q2))
        ec_h1 = dot(self._Bmat, hkl1)
        ec_h2 = dot(self._Bmat, hkl2)
        self.log.debug('ec_h1 = %s, ec_h2 = %s' % (ec_h1, ec_h2))
        ec_r1 = dot(d1_inv, ec_q1)
        ec_r2 = dot(d2_inv, ec_q2)
        self.log.debug('ec_r1 = %s, ec_r2 = %s' % (ec_r1, ec_r2))
        return self.calc_orient(ec_h1, ec_h2, ec_r1, ec_r2)
