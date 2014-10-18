#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#
#
# *****************************************************************************

"""NICOS Sample related usercommands"""

import json

from nicos import session
from nicos.core import UsageError, ConfigurationError
from nicos.commands import usercommand
from nicos.utils import printTable
from nicos.pycompat import urllib


ACTIVATIONURL = 'https://www.frm2.tum.de/intranet/activation/'


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
        printTable(['instrument'], [(d, ) for d in data['instruments']], session.log.info)

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
