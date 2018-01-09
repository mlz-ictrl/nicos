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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.core import Readable, Moveable, Param, Attach, oneof, listof, \
    InvalidValueError, dictof, anytype
from nicos.pycompat import iteritems


# Storage structure of tunewave tables:
# {measmode: {wavelength: {echotime: {tunedev : value}}}}


class EchoTime(Moveable):
    """Reseda echo time device.
    Provides storage and access to tunewave tables which are used to determine
    the device setup for the particular echo time, considering the measurement
    mode and the current wavelength."""

    attached_devices = {
        'wavelength': Attach('Wavelength device', Readable),
        'dependencies': Attach('Echo time dependent devices', Readable,
                               multiple=True),
    }

    parameters = {
        'tables': Param('Tune wave tables',
                        type=dictof(oneof('nrse', 'mieze'), dictof(float,
                                    dictof(float, dictof(str, anytype)))),
                        settable=True, userparam=False),
        'currenttable': Param('Currently used tune wave tables',
                              type=dictof(float, dictof(str, anytype)),
                              settable=False, userparam=True, volatile=True),
        'tunedevs': Param('Devices used for tuning',
                          type=listof(str), settable=False, userparam=False,
                          volatile=True),
        'availtables': Param('Available tunewave tables',
                             type=dictof(str, listof(float)), settable=False,
                             userparam=False, volatile=True),
        'wavelengthtolerance': Param('Wavelength tolerance for table'
                                     'determination', type=float, settable=True,
                                     default=0.1),
    }

    valuetype = float

    def doPreinit(self, mode):
        # create an internal lookup dictionary for tunedevs ({name: dev})
        self._tunedevs = {entry.name: entry
                          for entry in self._attached_dependencies}

    def doRead(self, maxage=0):
        # read all tuning devices
        devs = {key: value.read(maxage)
                for key, value in iteritems(self._tunedevs)}

        # find correct echotime for current device setup in currently active
        # tunewave table
        for echotime, tunedevs in iteritems(self.currenttable):
            self.log.debug('%s', echotime)
            success = True
            for tunedev, value in iteritems(tunedevs):
                # fuzzy matching necessary due to maybe oscillating devices
                prec = getattr(self._tunedevs[tunedev], 'precision', 0)
                if not self._fuzzy_match(value, devs.get(tunedev, None), prec):
                    self.log.debug('%s', tunedev)
                    success = False
                    break
            if success:
                return echotime

        # return 0 as echotime and show additional info in status string
        # if the echo time could not be determined
        return 0.0

    def doStart(self, value):
        # filter unsupported echotimes
        if value not in self.currenttable:
            raise InvalidValueError('Given echo time not supported by current '
                                    'tunewave table (%s/%s)'
                                    % (session.experiment.measurementmode,
                                       self._attached_wavelength.read()))

        # move all tuning devices at once without blocking
        for tunedev, val in iteritems(self.currenttable[value]):
            self._tunedevs[tunedev].move(val)

    def doReadTunedevs(self):
        return sorted(self._tunedevs)

    def doReadAvailtables(self):
        return {key: sorted(value) for key, value in iteritems(self.tables)}

    def doReadCurrenttable(self):
        cur_wavelength = self._attached_wavelength.read()

        precision = self.wavelengthtolerance
        table = self.tables.get(session.experiment.measurementmode, {})

        # determine current tunewave table by measurement mode and fuzzy
        # matched wavelength
        for wavelength, tunewavetable in iteritems(table):
            if self._fuzzy_match(cur_wavelength, wavelength, precision):
                return tunewavetable

        return {}

    def getTable(self, measurement_mode, wavelength):
        """Get a specific tunewave table. Avoid transfering all tables for each
        access."""
        return self.tables.get(measurement_mode, {}).get(wavelength, {})

    def setTable(self, measurement_mode, wavelength, table):
        """Set a specific tunewave table. Avoid transfering all tables for each
        access."""

        # validate table structure and device values
        table = self._validate_table(table)

        # use ordinary dicts instead of readonlydicts to be able to change them
        tables = dict(self.tables)
        mode_table = dict(tables.setdefault(measurement_mode, {}))

        # ensure float for wavelength value due to later fuzzy matching
        mode_table[float(wavelength)] = table
        tables[measurement_mode] = mode_table

        self.tables = tables

    def deleteTable(self, measurement_mode, wavelength):
        """Delete a specific tunewave table. Avoid transfering all tables for
        each access."""

        # use ordinary dicts instead of readonlydicts to be able to change them
        tables = dict(self.tables)
        tables[measurement_mode] = dict(tables.get(measurement_mode, {}))
        del tables[measurement_mode][float(wavelength)]
        self.tables = tables

    def _fuzzy_match(self, value, setpoint, precision):
        """General fuzzy matching of values (used for float comparisons)."""
        return (value >= (setpoint - precision)
                and value <= (setpoint + precision))

    def _validate_table(self, table):
        """Validates the structure of a single tunewave table and and all the
        included device values (using the valuetype of the particular device).
        """
        # Structure of a single tunewave table: {echotime: {tunedev : value}}

        result = {}
        for echotime, tunedevs in iteritems(table):
            echotime = float(echotime)
            result[echotime] = {}
            for tunedev, value in iteritems(tunedevs):
                result[echotime][tunedev] = self._tunedevs[tunedev].valuetype(value)

        return result
