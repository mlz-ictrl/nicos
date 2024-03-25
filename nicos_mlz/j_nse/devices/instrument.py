# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

import csv

from nicos.core import Param
from nicos.core.constants import MASTER
from nicos.devices.instrument import Instrument


t_noms = {
    't_act': None,
    'pow01': None, 'pow02': None, 'pow03': None, 'pow04': None, 'pow05': None,
    'pow06': None, 'pow07': None, 'pow08': None, 'pow09': None, 'pow10': None,
    'pow11': None, 'pow12': None, 'pow13': None,
    'pow16': None, 'pow17': None, 'pow18': None, 'pow19': None, 'pow20': None,
    'pow21': None, 'pow22': None, 'pow23': None, 'pow24': None, 'pow25': None,
    'pow26': None, 'pow27': None, 'pow28': None, 'pow29': None, 'pow30': None,
                   'pow32': None, 'pow33': None, 'pow34': None, 'pow35': None,
    'pow36': None, 'pow37': None, 'pow38': None,
    'dum1': None, 'dum2': None, 'dum3': None,
    'countscale': None, 'J': None,
}
qs = {
    'mophi': None, 'mogamma': None, 'mobeta': None, 'mopsi': None, 't_nom': {},
}
lambdas = {
    'dlambda': None, 'phase_deg_perA1': None, 'phase_deg_perA2': None,
    'selector': None, 'Q': {},
}
template = {
    'Lambda': {}, 'moana': None,
    'mo_cc11a': None, 'mo_cc11b': None, 'mo_cc12a': None, 'mo_cc12b': None,
    'mo_cc21a': None, 'mo_cc21b': None, 'mo_cc22a': None, 'mo_cc22b': None,
    'mo_cc31a': None, 'mo_cc31b': None, 'mo_cc32a': None, 'mo_cc32b': None,
}


class JnseInstrument(Instrument):
    """J-NSE instrument can parse and store NIST tables.
    """
    parameters = {
        'devices': Param(
            'List of settable devices for J-NSE experiment',
            type=list, settable=True, internal=True,
        ),
        'table': Param(
            'J-NSE experiment settings table',
            type=dict, settable=True, internal=True,
        ),
        'table_filename': Param(
            'filename for J-NSE experiment settings table',
            type=str, mandatory=True,
        ),
    }

    def doInit(self, mode):
        if mode == MASTER:
            self.devices, self.table = self._read_table()

    def _read_table(self):
        """Reads NIST_table.csv and returns list of devices and the device map.
        """
        with open(self.table_filename, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f, delimiter=',', skipinitialspace=True))
            keys = [key.split('/')[0].split(':')[0].strip() for key in rows[1]]
            table = {}
            for row in rows[2:]:
                lv = float(row[keys.index('Lambda')])
                qv = float(row[keys.index('Q')])
                tv = float(row[keys.index('t_nom')])
                for k, it in template.items():
                    i = keys.index(k)
                    if isinstance(it, dict):
                        if k not in table:
                            table[k] = {}
                        if lv not in table[k]:
                            table[k][lv] = {}
                    else:
                        table[k] = float(row[i])
                for k, it in lambdas.items():
                    i = keys.index(k)
                    if isinstance(it, dict):
                        if k not in table['Lambda'][lv]:
                            table['Lambda'][lv][k] = {}
                        if qv not in table['Lambda'][lv][k]:
                            table['Lambda'][lv][k][qv] = {}
                    else:
                        table['Lambda'][lv][k] = float(row[i])
                for k, it in qs.items():
                    i = keys.index(k)
                    if isinstance(it, dict):
                        if k not in table['Lambda'][lv]['Q'][qv]:
                            table['Lambda'][lv]['Q'][qv][k] = {}
                        if tv not in table['Lambda'][lv]['Q'][qv][k]:
                            table['Lambda'][lv]['Q'][qv][k][tv] = {}
                    else:
                        table['Lambda'][lv]['Q'][qv][k] = float(row[i])
                for k in t_noms:
                    i = keys.index(k)
                    table['Lambda'][lv]['Q'][qv]['t_nom'][tv][k] = float(row[i])
            return keys, table
