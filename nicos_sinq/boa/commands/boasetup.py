#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke, <mark.koennecke@psi.ch>
#
# *****************************************************************************


"""
This implements BOA configuration discovery. BOA has a very variable
instrument configuration. The system works like this:
1) Through an external script, the EPICS IOC is restarted
2) During startup, the EPICS IOC discovers the available hardware and
   sets a number of EPICS database fields informing about the presence
   of hardware.
3) This code reads those flags and compares them with the NICOS configuration.
   And then unloads and loads setups as required.
4) Where this is possible, the BOA tables are also reconfigured
5) At the end a messages is produced which tells the user about those bits
   which cannot be auto configured.

This whole stuff is very specific to BOA and tightly coupled with the IOC
configuration and startup.
"""

import epics

from nicos import session
from nicos.commands import usercommand
from nicos.commands.basic import AddSetup, RemoveSetup

# For some devices I can only test presence and not on which table they sit.
# This
# is backed by this list containing tuples of PV name and corresponding setup
test_presence = [('SQ:BOA:MCU4:PRESENT', 'adaptive_optics17'),
                 ('SQ:BOA:NGIV2:PRESENT', 'ngiv2'),
                 ('SQ:BOA:AGILENT:PRESENT', 'agilent')]

# For some devices EPICS can detect on which table they sit in addition to the
# test for presence. These devices are held in this list. There is a tuple of
# test PV name and matching setup here.
table_presence = [('SQ:BOA:xy1:TableIndex', 'translation1'),
                  ('SQ:BOA:xy1:TableIndex', 'translation2'),
                  ('SQ:BOA:drot1:TableIndex', 'drot1'),
                  ('SQ:BOA:drot2:TableIndex', 'drot2'),
                  ('SQ:BOA:dg:TableIndex', 'goniometer_g'),
                  ('SQ:BOA:sl1:TableIndex', 'slit1'),
                  ('SQ:BOA:sl2:TableIndex', 'slit2'),
                  ('SQ:BOA:sld:TableIndex', 'detector_slit'),
                  ('SQ:BOA:adap:TableIndex', 'adaptive_optics'),
                  ('SQ:BOA:ra:TableIndex', 'rotation_ra'),
                  ('SQ:BOA:gbl:TableIndex', 'goniometer_gbl'),
                  ('SQ:BOA:taz:TableIndex', 'translation_z')
                  ]

# BOA table names
tables = ['Table2', 'Table3', 'Table4', 'Table5', 'Table6']


@usercommand
def boadiscover():

    # IOC restart
    iocrestart = session.getDevice('iocrestart')
    iocrestart.maw(47)

    to_add = []
    to_remove = []
    loaded_setups = session.loaded_setups

    # presence testing
    for comp in test_presence:
        presence = epics.caget(comp[0], False)
        if presence == 1:
            if comp[1] not in loaded_setups:
                to_add.append(comp[1])
        else:
            if comp[1] in loaded_setups:
                to_remove.append(comp[1])

    # table testing
    table_config = {2: [], 3: [], 4: [], 5: [], 6: []}
    for comp in table_presence:
        idx = epics.caget(comp[0], False)
        if idx < 2:
            if comp[1] in loaded_setups:
                to_remove.append(comp[1])
        else:
            if comp[1] not in loaded_setups:
                to_add.append(comp[1])
            table_config[idx].append(comp[1])

    # Unload and load setups
    RemoveSetup(*to_remove)
    AddSetup(*to_add)

    # Configure tables
    for i in range(len(tables)):
        table_name = tables[i]
        table = session.getDevice(table_name)
        # remove setups which have gone
        for setup in to_remove:
            if setup in table.setups:
                table.removeSetup(setup)
        # add additional setups to table
        for setup in table_config[i+2]:
            if setup not in table.setups:
                table.addSetup(setup)

    session.log.info('Autodiscovery finished')
    session.log.info('Some setups: dmono, detectors etc cannot be auto '
                     'discovered and assigned to tables')


@usercommand
def find_unassigned():
    not_assignable = ['startup', 'table2', 'table3', 'table4', 'table5',
                      'table6', 'system', 'cache', 'daemon', 'poller',
                      'config']

    assigned = []
    for t in tables:
        table = session.getDevice(t)
        assigned = assigned + table.setups

    unassigned = []
    loaded_setups = session.loaded_setups

    for setup in loaded_setups:
        if setup not in assigned and setup not in not_assignable:
            unassigned.append(setup)
    if not unassigned:
        session.log.info('No unassigned setups')
    else:
        session.log.info('There are setups not assigned to tables:')
        session.log.info('  %s', str(unassigned))


@usercommand
def show_table_config():
    for t in tables:
        table = session.getDevice(t)
        session.log.info('%s  %s', t,  str(table.setups))
