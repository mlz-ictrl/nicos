# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.core.device import Readable
from nicos.devices.datasinks import FITSImageSink


class NIAGFitsSink(FITSImageSink):
    """
        A special version of the standard FITSImageSink which just writes the
        header in the form liked by the NIAG group @ PSI
    """

    def _buildHeader(self, info, hdu):
        devlist = [devname
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Readable)]

        self.log.debug('devlist : %s', devlist)

        setups = session.getSetupInfo()
        setups_log = {}

        self.log.debug('setup list: %s', list(setups.keys()))

        for s in setups:
            self.log.debug('setup "%s":', s)
            s_devlist = (setups[s])['devices']
            self.log.debug(s_devlist)
            s_devlist = [d for d in s_devlist if d in devlist]
            self.log.debug(s_devlist)
            for d in s_devlist:
                setups_log.setdefault(s, [])
                setups_log[s].append(session.devices[d])

        self.log.debug(str(setups_log))

        for s in setups_log.values():
            for dev in s:

                # The FITS standard defines max 8 characters for a header key.
                # To make longer keys possible, we use the HIERARCH keyword
                # here (67 chars max).
                # To get a consistent looking header, add it to every key
                key = 'HIERARCH ' + s + '/' + dev.name

                # use only ascii characters and escapes if necessary.
                try:
                    val = dev.read(0)
                    value = dev.format(val, unit=True).encode('unicode-escape')
                except Exception as e:
                    session.log.warning('Failed to read dev.name, %s,'
                                        ' with %s, Offending value: %s',
                                        dev.name, e, val)
                    value = 'Unknown'

                # Determine maximum possible value length (key dependend).
                maxValLen = 63 - len(key)

                # Split the dataset into several header entries if necessary
                # (due to the limited length)
                splittedHeaderItems = [value[i:i + maxValLen]
                                       for i in
                                       range(0, len(value), maxValLen)]

                for item in splittedHeaderItems:
                    hdu.header.append((key, str(item)))
