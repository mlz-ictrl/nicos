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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import pyfits

from nicos import session
from nicos.core import DataSink, ImageProducer
from nicos.pycompat import OrderedDict, iteritems
from nicos.devices.generic import FreeSpace


# XXX: to be rewritten with the new interface

class ImageStorageFits(ImageProducer):

    def _readImageFromHw(self):
        raise NotImplementedError('please implement _readImageFromHw() in %s'
                                  % self.__class__.__name__)

    def doRead(self, maxage=0):
        return self.lastfilename

    def doSimulate(self, preset):
        return [self.lastfilename]

    def doSave(self, exception=False):
        # query data
        headerData = self._collectHeaderData()
        imgData = self._readImageFromHw()

        # create hdu from image
        hdu = pyfits.PrimaryHDU(imgData)

        # add header entries
        for key, value in iteritems(headerData):
            # Add HIERARCH keyword to make long keys possible.
            # To get a consistent looking header, add it to every key.
            key = ('HIERARCH %s' % key).strip()
            value = ''.join(char for char in str(value) if 31 < ord(char) < 128).strip()

            # Split the value into multiple header entries if necessary
            maxValLen = 63 - len(key)
            entries = [value[i:i + maxValLen] for i in range(0, len(value), maxValLen)]

            # append header entries
            for entry in entries:
                self.log.debug('Set hkead: %s = %s' % (key, entry))
                hdu.header.append((key, entry))

        # write fits file
        self.log.debug('Save fits image to: %s' % self.lastfilename)
        hdu.writeto(self.lastfilename)

        # notify clients of new data (we only send the file name, not the actual
        # data; the client has to get the data out of the file from the filesystem)
        session.updateLiveData('fits', self.lastfilename, '', 0, 0, 0, 0, '')

    def _collectHeaderData(self):
        data = OrderedDict()

        # session info
        data['setups'] = [entry for entry in session.loaded_setups]
        data['devices'] = session.devices.keys()

        # Query parameters and current value of all interesting devices
        for deviceName, device in iteritems(session.devices):

            # Skip Experiment, DataSink, FreeSpace and lowlevel devices
            if isinstance(device, (DataSink, FreeSpace)) \
                or device.lowlevel:
                continue

            # Query important info
            for _category, key, value in device.info():
                data['%s_%s' % (deviceName, key)] = value

        return data
