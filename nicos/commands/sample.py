#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS Sample related usercommands"""

import json
from copy import deepcopy

from numpy import sqrt, pi, sin, exp, log, arcsin, radians, degrees

from nicos import session
from nicos.core import UsageError, ConfigurationError
from nicos.commands import usercommand
from nicos.commands.output import printinfo, printwarning
from nicos.utils import printTable
from nicos.utils.analyze import estimateFWHM
from nicos.pycompat import urllib
from nicos.utils.fitting import Fit
from nicos.devices.tas.spacegroups import can_reflect, get_spacegroup

ACTIVATIONURL = 'https://webapps.frm2.tum.de/intranet/activation/'


@usercommand
def activation(formula=None, instrument=None,
               flux=None, cdratio=0, fastratio=0,
               mass=None, exposure=24, getdata=False):
    """Calculate sample activation using the FRM II activation web services.

        ``formula``:
           the chemical formula,  see below for possible formats

        The *flux* can be specified either by:

            ``instrument``:
                the instrument name to select flux data

        or:

            ``flux``:
                The thermal flux (for cold instruments use the equivalent
                thermal flux)
            ``cdratio``:
                The ratio between full flux and flux with 1mm Cd in the beam,
                0 to deactivate
            ``fastratio``:
                Thermal/fast neutron ratio, 0 to deactivate

        ``mass``:
            the sample mass in g

        ``exposure``:
            exposure time in h, default 24h

        ``getdata``:
            In addition to printing the result table,
            return a dict with the full results for  further
            processing

        **Formula input format**

        Formula:
              ``CaCO3``

        Formula with fragments:
             ``CaCO3+6H2O``

        Formula with parentheses:
            ``HO ((CH2)2O)6 H``

        Formula with isotope:
            ``CaCO[18]3+6H2O``

        Counts can be integer or decimal:
            ``CaCO3+(3HO1.5)2``

        Mass fractions use %wt, with the final portion adding to 100%:
            ``10%wt Fe // 15% Co // Ni``

        Volume fractions use %vol, with the final portion adding to 100%:
            ``10%vol Fe@8.1 // Ni@8.5``

            For volume fractions you have to specify the density using
            ``@<density>``!

        Mixtures can nest. The following is a 10% salt solution by weight \
        mixed 20:80 by volume with D2O:
            ``20%vol (10%wt NaCl@2.16 // H2O@1) // D2O@1``
    """

    if formula is None:
        try:
            #  preparation for a future enhanced sample class
            formula = session.experiment.sample.formula
        except (ConfigurationError, AttributeError):
            # ConfigurationError is raised if no experiment is in session
            pass
    if formula is None:
        raise UsageError('Please give a formula')
    if flux:
        instrument = 'Manual'
    if instrument is None:
        try:
            instrument = session.instrument.instrument or None
        except ConfigurationError:
            pass
    if instrument is None:
        raise UsageError('Please specifiy an instrument or flux')
    if mass is None:
        try:
            formula = session.experiment.sample.mass
        except (ConfigurationError, AttributeError):
            pass
    if mass is None:
        raise UsageError('Please specify the sample mass')

    qs = '?json=1&formula=%(formula)s&instrument=%(instrument)s&mass=%(mass)g' \
        % locals()
    if flux:
        qs += '&fluence=%(flux)f&cdratio=%(cdratio)f&fastratio=%(fastratio)f' \
            % locals()
    qs = ACTIVATIONURL + qs
    try:
        response = urllib.request.urlopen(qs)
    except urllib.error.HTTPError as e:
        session.log.warning('Error opening: %s' % qs)
        session.log.warning(e)
        return None
    data = json.load(response)
    if data['ecode'] == 'unknown instrument' and flux is None:
        session.log.warning('Instrument %(instrument)s unknown to calculator, '
                            'specify flux manually' % locals())
        session.log.info('Known instruments')
        printTable(['instrument'], [(d, ) for d in data['instruments']],
                   session.log.info)

    if data['result']['activation']:
        h = data['result']['activation']['headers']
        th = [h['isotope'], h['daughter'], h['reaction'], h['Thalf_str']]
        for ha in h['activities']:
            th.append(ha)
        rows = []
        for r in data['result']['activation']['rows']:
            rd = [r['isotope'], r['daughter'], r['reaction'], r['Thalf_str']]
            for a in r['activities']:
                rd.append('%.3g' % a if a > 1e-6 else '<1e-6')
            rows.append(rd)
        dr = ['', '', '', 'Dose (uSv/h)']
        for d in data['result']['activation']['doses']:
            dr.append('%.3g' % d)
        rows.append(dr)

        printTable(th, rows, session.log.info)
    else:
        session.log.info('No activation')
    if getdata:
        return data
    return


def _extract_powder_data(num, dataset):
    values = dict(('%s_%s' % (dev, key), value)
                  for key in dataset.headerinfo
                  for (dev, key, value) in dataset.headerinfo[key])
    if 'ki_value' not in values:
        if 'mono_value' not in values:
            printwarning('dataset %d has no ki or mono value' % num)
            return
        ki = values['mono_value']
    else:
        ki = values['ki_value']
    ki = float(ki.split()[0])

    # x column
    for sttname in ['stt', 'phi']:
        if sttname in dataset.xnames:
            i = dataset.xnames.index(sttname)
            xs = [line[i] for line in dataset.xresults]
            break
    else:
        printwarning('dataset %d has no 2-theta X values' % num)
        return

    # normalization column (monitor > timer)
    mcol = None
    try:
        # ignore monitors with smaller count
        mcol = sorted([(dataset.yresults[0][j], j)
                       for j in range(len(dataset.ynames))
                       if dataset.yvalueinfo[j].type == 'monitor'])[-1][1]
    except IndexError:
        mcol = None
    # if highest monitor count is zero, prefer time
    if mcol is None or (dataset.yresults[0][mcol] == 0):
        try:
            mcol = [j for j in range(len(dataset.ynames))
                    if dataset.yvalueinfo[j].type == 'time'][0]
        except IndexError:
            printwarning('dataset %d has no column of type "monitor" '
                         'or "time"' % num)
            return
    ms = [float(line[mcol]) for line in dataset.yresults]

    # y column
    try:
        ycol = [j for j in range(len(dataset.ynames))
                if dataset.yvalueinfo[j].type == 'counter'][0]
    except IndexError:
        printwarning('dataset %d has no Y column of type "counter"' % num)
    else:
        ys = [line[ycol] for line in dataset.yresults]

        if dataset.yvalueinfo[ycol].errors == 'sqrt':
            dys = [sqrt(y) for y in ys]
        elif dataset.yvalueinfo[ycol].errors == 'next':
            dys = [line[ycol+1] for line in dataset.yresults]
        else:
            dys = [1] * len(ys)

    ys = [y/m for (y, m) in zip(ys, ms)]
    dys = [dy/m for (dy, m) in zip(dys, ms)]

    numfitpoints = 5
    if len(xs) < numfitpoints:
        printwarning('not enough datapoints in scan %d' % num)
        return
    # now try to fit the peaks
    peaks = []  # collects infos for all peaks we will find...

    fwhm, xpeak, ymax, ymin = estimateFWHM(xs, ys)
    initpars = [ymax - ymin, xpeak, fwhm, ymin]

    def model(x, a, c, w, b):
        return abs(b) + abs(a)*exp(-log(2)*(x-c)**2/(2*w)**2)

    fit = Fit(model, ['a', 'c', 'w', 'b'], initpars)
    res = fit.run('', xs, ys, dys)
    if res._failed:
        printwarning('no Gauss fit found in dataset %d' % num)
        return
    peaks.append([res.c, res.dc])
    return ki, peaks


@usercommand
def powderfit(powder, scans=None, peaks=None, ki=None, dmono=3.355, spacegroup=1):
    """Fit powder peaks of a cubic powder sample to calibrate instrument
    wavelength.

    First argument is either a string that names a known material (currently
    only ``'YIG'`` is available) or a cubic lattice parameter.  Then you need to
    give either scan numbers (*scans*) or peak positions (*peaks*) and a neutron
    wavevector (*ki*).  Examples:

    >>> powderfit('YIG', scans=[1382, 1383, 1384, ...])

    >>> powderfit(12.377932, peaks=[45.396, 61.344, 66.096, ...], ki=1.4)

    As a further argument, *dmono* is the lattice constant of the monochromator
    (only used to calculate monochromator 2-theta offsets), it defaults to PG
    (3.355 A).
    """
    maxhkl = 10    # max H/K/L to consider when looking for d-values
    maxdd = 0.2    # max distance in d-value when looking for peak indices
    ksteps = 50    # steps with different ki
    dki = 0.002    # relative ki stepsize

    if powder == 'YIG':
        a = 12.377932
        spacegroup = 230
        printinfo('YIG: using cubic lattice constant of %.6f A' % a)
        printinfo()
    else:
        if not isinstance(powder, float):
            raise UsageError('first argument must be either "YIG" or a '
                             'lattice constant')
        a = powder

    sg = get_spacegroup(spacegroup)
    # calculate (possible) d-values
    # loop through some hkl-sets, also consider higher harmonics...
    dhkls = {}
    for h in range(maxhkl):
        for k in range(maxhkl):
            for l in range(maxhkl):
                if h + k + l > 0:  # assume all reflections are possible
                    if not can_reflect(sg, h, k, l):
                        continue
                    G = sqrt(h*h + k*k + l*l)
                    dhkls[a/G] = '(%d %d %d)' % (h, k, l)
                    dhkls[a/(2*G)] = '(%d %d %d)/2' % (h, k, l)
                    dhkls[a/(3*G)] = '(%d %d %d)/3' % (h, k, l)
                    dhkls[a/(4*G)] = '(%d %d %d)/4' % (h, k, l)
                    dhkls[a/(5*G)] = '(%d %d %d)/5' % (h, k, l)
    # generate list from dict
    dvals = sorted(dhkls)

    # fit and helper functions

    def dk2tt(d, k):
        return 2.0 * degrees(arcsin(pi/(d * k)))

    def model(x, k, stt0):
        return stt0 + dk2tt(x, k)

    data = {}
    if not peaks:
        if not scans:
            raise UsageError('please give either scans or peaks argument')

        for dataset in session.experiment._last_datasets:
            num = dataset.sinkinfo.get('number')
            if num not in scans:
                continue
            res = _extract_powder_data(num, dataset)
            if res:
                ki, peaks = res  # pylint: disable=W0633
                data.setdefault(ki, []).extend([None, p, dp, '#%d ' % num]
                                               for (p, dp) in peaks)
        if not data:
            printwarning('no data found, check the scan numbers!')
            return
    else:
        if scans:
            raise UsageError('please give either scans or peaks argument')
        if not ki:
            raise UsageError('please give ki argument together with peaks')
        data[float(ki)] = [[None, p, 0.1, ''] for p in peaks]

    beststt0s = []
    bestmtt0s = []
    bestrms = 0.1
    bestlines = []
    orig_data = data
    for j in [0] + [i * s for i in range(1, ksteps) for s in (-1, 1)]:
        out = []
        p = out.append
        data = deepcopy(orig_data)

        # now iterate through data (for all ki and for all peaks) and try to
        # assign a d-value assuming the ki not to be completely off!
        for ki in sorted(data):
            new_ki = ki + j*dki*ki
            # iterate over ki specific list, start at last element
            for el in reversed(data[ki]):
                tdval = pi/new_ki/sin(radians(el[1]/2.))  # dvalue from scan
                distances = [(abs(d-tdval), i) for (i, d) in enumerate(dvals)]
                mindist = min(distances)
                if mindist[0] > maxdd:
                    p('%speak at %7.3f -> no hkl found' % (el[3], el[1]))
                    data[ki].remove(el)
                else:
                    el[0] = dvals[mindist[1]]
                    p('%speak at %7.3f could be %s at d = %-7.4f' %
                      (el[3], el[1], dhkls[el[0]], el[0]))
        p('')

        restxt = []
        restxt.append('___final_results___')
        restxt.append('ki_exp  #peaks | ki_fit   dki_fit  mtt_0    lambda   | '
                      'stt_0    dstt_0   | chisqr')
        stt0s = []
        mtt0s = []
        rms = 0
        for ki in sorted(data):
            new_ki = ki + j*dki*ki
            peaks = data[ki]
            fit = Fit(model, ['ki', 'stt0'], [new_ki, 0])
            res = fit.run('', [el[0] for el in peaks], [el[1] for el in peaks],
                          [el[2] for el in peaks])
            if res._failed:
                restxt.append('%4.3f   %-6d | No fit!' % (ki, len(peaks)))
                rms += 1e6
                continue
            mtt0 = dk2tt(dmono, res.ki) - dk2tt(dmono, ki)
            restxt.append('%5.3f   %-6d | %-7.4f  %-7.4f  %-7.4f  %-7.4f  | '
                          '%-7.4f  %-7.4f  | %.2f' %
                          (ki, len(peaks), res.ki, res.dki, mtt0, 2*pi/res.ki,
                           res.stt0, res.dstt0, res.chi2))
            stt0s.append(res.stt0)
            mtt0s.append(mtt0)
            peaks_fit = [model(el[0], res.ki, res.stt0) for el in peaks]
            p('___fitted_peaks_for_ki=%.3f___' % ki)
            p('peak       dval     measured fitpos   delta')
            for i, el in enumerate(peaks):
                p('%-10s %-7.3f  %-7.3f  %-7.3f  %-7.3f%s' % (
                    dhkls[el[0]], el[0], el[1], peaks_fit[i], peaks_fit[i] - el[1],
                    '' if abs(peaks_fit[i] - el[1]) < 0.10 else " **"))
            p('')
            rms += sum((pobs - pfit)**2 for (pobs, pfit) in
                       zip([el[1] for el in peaks], peaks_fit)) / len(peaks)

        out.extend(restxt)

        if rms < bestrms:
            beststt0s = stt0s
            bestmtt0s = mtt0s
            bestrms = rms
            bestlines = out

    if len(beststt0s) == 0:
        printwarning('no fitted offsets available')
        return

    for line in bestlines:
        printinfo(line)

    meanstt0 = sum(beststt0s)/len(beststt0s)
    meanmtt0 = sum(bestmtt0s)/len(bestmtt0s)

    printinfo('Check errors (dki, dstt0)!')
    printinfo('')
    printinfo('Adjust using:')
    printinfo('mtt.offset += %.4f' % meanmtt0)
    printinfo('mth.offset += %.4f' % (meanmtt0/2))
    printinfo('stt.offset += %.4f' % meanstt0)
