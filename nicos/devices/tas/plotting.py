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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""
Plotting tools for triple-axis spectrometers.
"""

from __future__ import print_function

import os
import time
from fractions import gcd

from numpy import array, linspace, sqrt, delete, sin, cos, arctan2, mat, cross

from nicos.core import ComputationError
from nicos.devices.tas.cell import CellBase
from nicos.devices.tas.rescalc import resmat as resmat_class
from nicos.devices.tas.spectro import THZ2MEV
from nicos.devices.tas.spacegroups import get_spacegroup, can_reflect


def pylab_key_handler(event):
    import pylab
    if event.key == 'p':
        # write temporary file in tmp directory of system
        filename = '/tmp/tas%s.ps' % time.strftime('%j%H%M')
        pylab.savefig(filename, dpi=72, facecolor='w', edgecolor='w',
                      orientation='landscape', papertype='a4')
        res = os.system('lp %s' % filename)
        if res == 0:
            print('Successfully sent file %s to the printer!' % filename)
        else:
            print('Error on sending file %s to the printer!' % filename)

    elif event.key == 'e':
        # create more or less unique filename
        filename = '/tmp/tas%s.pdf' % time.strftime('%j%H%M')
        pylab.savefig(filename, dpi=72, facecolor='w', edgecolor='w',
                      orientation='landscape', papertype='a4')
        print('Successfully exported file %s!' % filename)

    elif event.key == 'q':
        pylab.close()


class SpaceMap(object):

    def __init__(self, resmat, tasinfo, E=0, ki=None, kf=None, scan=None, **kwds):
        self.resmat = resmat
        self.tasinfo = tasinfo
        self.cell = CellBase()
        self.cell._setall(tasinfo['lattice'], tasinfo['angles'],
                          tasinfo['orient1'], tasinfo['orient2'],
                          tasinfo['psi0'])

        self.taus = []
        self.hkls = []
        for kwd in kwds:
            if kwd.startswith('tau'):
                self.taus.append(kwds[kwd])
            elif kwd.startswith('hkl'):
                self.hkls.append(kwds[kwd])

        mode = self.tasinfo['scanmode']
        const = self.tasinfo['scanconstant']
        if ki is not None:
            mode = 'CKI'
            const = ki
        if kf is not None:
            mode = 'CKF'
            const = kf
        self.E = E
        self.ny = self._thz(E)
        self.mode = mode
        self.const = const
        self.scan = scan

    def _thz(self, E):
        if self.tasinfo['energytransferunit'] == 'meV':
            return E / THZ2MEV
        return E

    def plot_hkl(self, hkl, label=None, **props):
        import pylab
        x, y, z = self.cell.hkl2Qcart(*hkl)
        if abs(z) > 0.0001:
            return
        pylab.scatter([x], [y], **props)
        if label is not None:
            pylab.text(x, y-0.1, label, size='x-small',
                       horizontalalignment='center', verticalalignment='top')

    def plot_hkls(self, hkls, labels=None, **props):
        import pylab
        xs, ys, indices = [], [], []
        for i, hkl in enumerate(hkls):
            x, y, z = self.cell.hkl2Qcart(*hkl[:3])
            if abs(z) > 0.0001:
                continue
            xs.append(x)
            ys.append(y)
            indices.append(i)
        if not xs:
            return
        pylab.scatter(xs, ys, **props)
        if labels is not None:
            for i, x, y in zip(indices, xs, ys):
                pylab.text(x, y-0.1, labels[i], size='x-small',
                           horizontalalignment='center', verticalalignment='top')

    def check_hkls(self, hkls):
        allowed = []
        limited = []
        for hkl in hkls:
            if len(hkl) == 4:
                hkl, E = list(hkl[:3]), hkl[3]
            else:
                hkl, E = list(hkl), self.E
            ny = self._thz(E)
            try:
                angles = self.cell.cal_angles(hkl, ny, self.mode, self.const,
                    self.tasinfo['scatteringsense'][1],
                    self.tasinfo['axiscoupling'], self.tasinfo['psi360'])
            except ComputationError:
                continue
            ok = True
            for devname, value in zip(['mono', 'ana', 'phi', 'psi', 'alpha'], angles):
                lim = self.tasinfo[devname + 'lim']
                if lim is not None and not lim[0] <= value <= lim[1]:
                    ok = False
                    break
            if ok:
                allowed.append(hkl)
            else:
                limited.append(hkl)
        return allowed, limited

    def generate_hkls(self, offset=None, origin=False, sgroup=True):
        if offset is None:
            offset = array([0, 0, 0])
        else:
            offset = array(offset)
        o1 = array(self.cell._orient1)
        o2 = array(self.cell._orient2)
        hkls = []
        sg = None
        if sgroup:
            sg = get_spacegroup(self.tasinfo['spacegroup'])
        for i in range(-10, 11):
            for j in range(-10, 11):
                base = i*o1 + j*o2
                if i == j == 0:
                    if not origin:
                        continue
                elif sg and not can_reflect(sg, *base):
                    continue
                hkls.append(base + offset)
        return self.check_hkls(hkls)

    def format_coord(self, x, y):
        h, k, l = self.cell.Qcart2hkl(array([x, y, 0]))
        return '( %.4f  %.4f  %.4f )  Q = %.4f A-1     ' % \
            (h, k, l, sqrt(x**2 + y**2))

    def plot_ellipsoid(self, hkl, x, y):
        import pylab
        # plot resolution ellipsoid in x-y plane
        self.resmat.sethklen(hkl[0], hkl[1], hkl[2], self.ny*THZ2MEV)
        xs1, ys1, xs2, ys2 = self.resmat.resellipse()[:4]
        # ellipse coordinate system is x || Q, y _|_ Q, so we need to find the
        # correct rotation matrix to project that onto the cartesian plane
        alpha = arctan2(y, x)
        matrix = mat([[cos(alpha), -sin(alpha)], [sin(alpha), cos(alpha)]])
        xs1, ys1 = array(matrix.dot(array([xs1, ys1])))
        xs2, ys2 = array(matrix.dot(array([xs2, ys2])))
        pylab.fill(xs1 + x, ys1 + y, color='blue', alpha=0.5)
        pylab.plot(xs2 + x, ys2 + y, color='green')
        plot_resatpoint(None, None, 'Resolution at selected HKL point',
                        resmat=self.resmat)

    def display_hkl(self, x, y, textobj):
        hkl = self.cell.Qcart2hkl(array([x, y, 0]))
        try:
            angles = self.cell.cal_angles(hkl, self.ny, self.mode, self.const,
                self.tasinfo['scatteringsense'][1], self.tasinfo['axiscoupling'],
                self.tasinfo['psi360'])
        except Exception as err:
            text = 'hkl = (%.4f %.4f %.4f) E = %.4f %s: impossible position: %s' % \
                (hkl[0], hkl[1], hkl[2], self.E, self.tasinfo['energytransferunit'], err)
            textobj.set_text(text)
            return None
        text = 'hkl = (%.4f %.4f %.4f) E = %.4f %s: %s = %.4f deg;  %s = %.4f deg' % \
            (hkl[0], hkl[1], hkl[2], self.E, self.tasinfo['energytransferunit'],
             self.tasinfo['phiname'], angles[2], self.tasinfo['psiname'], angles[3])
        textobj.set_text(text)
        return hkl

    def plot_map(self):
        import pylab

        # compile a list of reflexes allowed by current spectro config
        allowed, limited = self.generate_hkls()

        # calculate limits of movement from limits of phi and psi
        lim1, lim2, lim3, lim4 = [], [], [], []
        psimin, psimax = self.tasinfo['psilim']
        phimin, phimax = self.tasinfo['philim']
        coupling = self.tasinfo['axiscoupling']
        if self.mode == 'CKI':
            ki = self.const
            kf = self.cell.cal_kf(self.ny, ki)
        else:
            kf = self.const
            ki = self.cell.cal_ki1(self.ny, kf)
        for phival in linspace(phimin, phimax, 100):
            xy1 = self.cell.angle2Qcart([ki, kf, phival, psimin], coupling)
            xy2 = self.cell.angle2Qcart([ki, kf, phival, psimax], coupling)
            lim1.append(xy1[:2])
            lim2.append(xy2[:2])
        for psival in linspace(psimin, psimax, 100):
            xy1 = self.cell.angle2Qcart([ki, kf, phimin, psival], coupling)
            xy2 = self.cell.angle2Qcart([ki, kf, phimax, psival], coupling)
            lim3.append(xy1[:2])
            lim4.append(xy2[:2])

        # directions of axes
        dir1 = self.cell._orient1
        dir2 = cross(self.cell.cal_zone(), self.cell._orient1)
        # normalize second direction to smallest length
        comp = [abs(c) for c in dir2 if c != 0]
        complen = len(comp)
        if complen == 0:
            # should be impossible: all entries == 0, no change
            f = 1
        elif complen == 1:
            f = comp[0]
        elif complen == 2:
            f = gcd(comp[0], comp[1])
        else:
            f = min(gcd(comp[0], comp[1]), gcd(comp[1], comp[2]),
                    gcd(comp[0], comp[2]))
        dir2 /= f

        # set up pylab figure
        pylab.ion()
        pylab.figure('Reciprocal space visualization', figsize=(7, 7), dpi=120,
                     facecolor='1.0')
        pylab.clf()
        pylab.rc('text', usetex=True)
        pylab.rc('text.latex',
            preamble=r'\usepackage{amsmath}\usepackage{helvet}\usepackage{sfmath}')

        ax = pylab.subplot(111, aspect='equal')
        ax.set_axisbelow(True)  # draw grid lines below plotted points
        # register event handler to pylab
        pylab.connect('key_press_event', pylab_key_handler)
        def click_handler(event):
            if not event.inaxes: return
            canvas = pylab.gcf().canvas
            if canvas.toolbar.mode: return
            hkl = self.display_hkl(event.xdata, event.ydata, self.clicktext)
            if hkl is not None:
                self.plot_ellipsoid(hkl, event.xdata, event.ydata)
            canvas.draw()
        pylab.connect('button_release_event', click_handler)
        # monkey-patch formatting coordinates in the status bar
        pylab.gca().format_coord = self.format_coord

        pylab.title('Available reciprocal space for %s %.3f \\AA$^{-1}$, E = %.3f %s'
                    % (self.mode, self.const, self.E, self.tasinfo['energytransferunit']))
        pylab.xlabel('$Q_1$ (\\AA$^{-1}$) $\\rightarrow$ ( %d %d %d )' % tuple(dir1))
        pylab.ylabel('$Q_2$ (\\AA$^{-1}$) $\\rightarrow$ ( %d %d %d )' % tuple(dir2))
        pylab.grid(color='0.5', zorder=-2)
        if hasattr(pylab, 'tight_layout'):
            pylab.tight_layout()
        pylab.subplots_adjust(bottom=0.1)

        self.clicktext = pylab.text(0.5, 0.01, '(click to show angles)', size='small',
            horizontalalignment='center', transform=pylab.gcf().transFigure)

        # plot origin
        self.plot_hkl((0, 0, 0), color='black')
        # plot allowed Bragg indices
        self.plot_hkls(allowed, labels=['(%d%d%d)' % tuple(v) for v in allowed])
        # plot Bragg indices allowed by scattering plane, but limited by devices
        self.plot_hkls(limited, color='red')
        # plot user-supplied points
        for hkl in self.hkls:
            self.plot_hkl(hkl, color='#009900', edgecolor='black', linewidth=0.5,
                          label='(%.3g %.3g %.3g)' % tuple(hkl))
        # plot user-supplied propagation vectors
        for tau in self.taus:
            tau = array(tau)
            allowed1, limited = self.generate_hkls(tau, origin=True)
            allowed2, limited = self.generate_hkls(-tau, origin=True)
            self.plot_hkls(allowed1 + allowed2, color='#550055', s=3, marker='s')
        # plot user-supplied scan points
        if self.scan is not None:
            allowed, limited = self.check_hkls(self.scan)
            self.plot_hkls(allowed, color='#009900', s=2)
            self.plot_hkls(limited, color='red', s=2)
        # plot current spectrometer position
        current_pos = self.tasinfo['actpos']
        if abs(current_pos[3] - self.E) < 0.01:
            self.plot_hkls([current_pos[:3]], color='#990033', marker='x')
        # plot last calpos() result
        calpos = self.tasinfo['calpos']
        if calpos is not None and abs(calpos[3] - self.E) < 0.01:
            self.plot_hkls([calpos[:3]], color='#006600', marker='*')

        # plot limits of phi/psi
        for v in lim1, lim2, lim3, lim4:
            v = array(v)
            pylab.plot(v[:,0], v[:,1], color='0.7', zorder=-1)


def plot_hklmap(cfg, par, tasinfo, kwds):
    resmat = resmat_class(cfg, par)
    SpaceMap(resmat, tasinfo, **kwds).plot_map()


def plot_resatpoint(cfg, par, fignum='Resolution calculation', resmat=None):
    import pylab

    if resmat is None:
        resmat = resmat_class(cfg, par)

    x, y, xslice, yslice, xxq, yxq, xxqslice, yxqslice, xyq, yyq, xyqslice, yyqslice = \
        resmat.resellipse()

    pylab.ion()
    pylab.figure(fignum, figsize=(8.5, 6), dpi=120, facecolor='1.0')
    pylab.clf()
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
    pylab.plot(xxq, yxq)
    pylab.plot(xxqslice, yxqslice)

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
    text += r'\end{tabular}'
    t3 = pylab.text(-0.13, 1.0, text,
                    horizontalalignment='left', verticalalignment='top',
                    transform=ax3.transAxes)
    t3.set_size(10)


def plot_resscan(cfg, par, hkles, fignum='Scan resolution', resmat=None):
    import pylab

    if resmat is None:
        resmat = resmat_class(cfg, par)

    n = len(hkles)
    h, k, l, e = array(hkles).T

    pylab.ion()
    pylab.figure(5, figsize=(8.5, 6), dpi=120, facecolor='1.0')
    pylab.clf()
    pylab.rc('text', usetex=True)
    pylab.rc('text.latex',
             preamble='\\usepackage{amsmath}\\usepackage{helvet}\\usepackage{sfmath}')
    pylab.subplots_adjust(left=0.11, bottom=0.08, right=0.97, top=0.96,
                          wspace=0.25, hspace=0.39)
    # register event handler to pylab
    pylab.connect('key_press_event', pylab_key_handler)

    elliplist = []
    errors = []
    for i in range(n):
        resmat.sethklen(h[i], k[i], l[i], e[i])
        if not resmat.ERROR:
            elliplist.append(resmat.resellipse())
        else:
            print('%+1.4f %+1.4f %+1.4f %+1.4f => scattering triangle did not '
                  'close for this point => excluded from simulation' %
                  (h[i], k[i], l[i], e[i]))
            errors.append(i)

    # remove points for that scattering triangle did not close
    h = delete(h, errors)
    k = delete(k, errors)
    l = delete(l, errors)
    e = delete(e, errors)

    if len(e) > 1 and e[0] == e[1]: # q-scans plot energies as y axis
        q = 0.0
        if h[0] != h[1]:
            q = h
        elif k[0] != k[1]:
            q = k
        elif l[0] != l[1]:
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
