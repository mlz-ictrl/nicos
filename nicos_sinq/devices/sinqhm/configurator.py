#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from lxml import etree
from numpy import prod

from nicos.core import Attach, Device, Override, Param, listof, oneof
from nicos.pycompat import iteritems

from nicos_sinq.devices.sinqhm.connector import HttpConnector


class HistogramConfElement(Device):
    """ Basic element for configuring the histogram memory.
    Each element should be able to get a XML.
    """

    def getXml(self):
        raise NotImplementedError('Method needs to te implemented')

    def getXmlString(self, **config):
        return etree.tostring(self.getXml(), **config)


class HistogramConfArray(HistogramConfElement):
    """ Arrays for tof and lookup axis types are stored as separate
    entities within the XML file. The tag names must be those
    specified in the array attribute of the axis tag.

    The array tags itself has the following attributes:
    - rank: The number of dimensions of the array.
    - dim: A comma separated list of values describing the length
        of each dimension.

    Between the closing and ending array tag is the array data. This is
    just numbers. C storage order is assumed.

    Rank is automatically deduced from the length of the dimensions list.
    """
    parameters = {
        'tag': Param('Array tag for XML', type=str, mandatory=True),
        'dim': Param('Length of each dimension', type=listof(int),
                     mandatory=True, settable=True),
        'data': Param('Array data in each dimension',
                      type=listof(float), default=[], settable=True),
        'formatter': Param('Array data formatter', type=str),
        'threshold': Param('Threshold for the array', type=int,
                           settable=True),
        'offset': Param('Offset for the array', type=int, settable=True)
    }

    def setData(self, dim, data):
        """ Set the given data and dimensions. Checks if the dimensions
        match the data. In case a mismatch occurs the data and dims are
        not changed
        :param dim: (list) new shape of the array
        :param data: (list) Flattened list of the array (C Style, Row-Major)
        """
        if prod(dim) != len(data):
            self.log.error('Mismatch in dimensions and data length: '
                           'dims %s and data length %s', dim, len(data))
            return
        self.dim = dim
        self.data = data

    def dataText(self):
        """ The string that is used to write the data list in XML file.
        By default format the elements of list using the provided
        formatter and writes 5 elements every row.
        The subclasses can override this method and write in their own
        way.
        :return: (string) representation of the data vector
        """
        if not self.data:
            self.log.warning('Data for the array missing.')
            return ''

        arraytxt = '\n'
        newlinecount = 0
        for d in self.data:
            arraytxt += self.formatter % d
            newlinecount += 1
            if newlinecount % 5 == 0:
                newlinecount = 0
                arraytxt += '\n'
        arraytxt += '\n'
        return arraytxt

    def getXml(self):
        elem = etree.Element(self.tag, rank=str(len(self.dim)),
                             dim=','.join([str(d) for d in self.dim]))
        elem.text = self.dataText()
        return elem


class HistogramConfTofArray(HistogramConfArray):
    """ Special configuration array that stores the TOF values.
    The data vector represents the time bins. This class provides
    a way to change the time bins.
    """
    parameter_overrides = {
        'tag': Override(mandatory=False, default='tof'),
        'data': Override(type=listof(int)),
    }

    def updateTimeBins(self, tmin, tstep, channels):
        """ Update the time binning represented using this class.
        :param tmin: minimum time value
        :param tstep: time step
        :param channels: number of channels to use
        """
        data = range(tmin, tmin + tstep * channels, tstep)
        self.setData([channels], data)


class HistogramConfAxis(HistogramConfElement):
    """ This element describes an axis of the histogram memory.
    The axis tag has the following attributes:
    *length*: The length of the axis.
    *mapping*: The mapping type of the axis.
        Currently supported mapping types are:
        direct:  Detector number in packet is detector number in histogram.
        calculate:  The detector number in the histogram memory must be
            calculated from the data in the packet. If calculate has been
            selected, the following additional attribute to axis are evaluated:
            - multiplier A multiplier
            - divisor A divisor
            - preoffset An offset to apply before division or multiplication.
            - postoffset An offset to apply after division or multiplication.
            The formula to arrive at the histogram memory detector number d
            from the value in the packet p is:
            d = postoffset + (preoffset + p ∗ multiplier)/divisor
            If any of the parameters are not given or 0, then the operation
            is not performed: i.e. without a divisor no division.
        boundary: The histogram memory detector position is deduced through
            lookup in an array of bin boundaries. These boundaries must not
            necessarily be linear. This mode is commonly applied to time of
            flight data. This array should have length+1 bin boundary entries.
        lookuptable: This is for an area detector where the lookup for y is
        not independent of x. A 2D lookup array is required.
    *array*: Some axis mappings, tof, lookup, need arrays for their data.
        This attribute gives the name of the array to use.

    Additionally an axis can provide information about it's unit and label
    using parameters. The arrays associated with this axis need to be
    specified using the *array* attached device.

    If the array is not used, the bins can also be specified using the
    parameter *bins*. The parameter *bin* returns the array data
    if array is attached, otherwise the cached value.
    """
    parameters = {
        'length': Param('Length of the axis', type=int, volatile=True),
        'bins': Param('Binning information of the axis', type=list,
                      volatile=True),
        'mapping': Param('The mapping type of the axis',
                         type=oneof('direct', 'calculate', 'boundary',
                                    'lookuptable')),
        'multiplier': Param('Multiplier in case mapping is calculate',
                            type=int),
        'divisor': Param('Divisor in case mapping is calculate', type=int),
        'preoffset': Param('Offset to apply before division/multiplication',
                           type=int),
        'postoffset': Param('Offset to apply after division/multiplication',
                            type=int),
        'unit': Param('Unit for the axis', type=str),
        'label': Param('Label for the axis', type=str)
    }

    attached_devices = {
        'array': Attach('Arrays configured for this axis e.g. mappings, tof, '
                        'lookup table', HistogramConfArray, optional=True)
    }

    # The parameters that can appear as XML attributes
    xml_params = ['length', 'mapping', 'multiplier', 'divisor', 'preoffset',
                  'postoffset']

    def doReadLength(self):
        # In case an array is attached the length of the axis is automatically
        # deduced from the length of the array
        if self._attached_array:
            arraylen = len(self._attached_array.data)
            if arraylen == 0:
                self.log.warning('Data not configured in the array: %s!',
                                 self._attached_array.name)
                return 0
            # If mapping is boundary then length is 1 less than size of array
            if self.mapping == 'boundary':
                arraylen = arraylen - 1
            return arraylen
        else:
            return self._getFromCache('length', lambda x: 1)

    def doReadBins(self):
        # In case array is attached use that as bins
        if self._attached_array:
            return self._attached_array.data
        else:
            return self._getFromCache('bins', lambda x: [])

    def getXmlAttrs(self):
        """ Get the XML attributes for the axis
        """
        attrs = {}
        for par in self.xml_params:
            if getattr(self, par, None):
                attrs[par] = getattr(self, par)

        if self._attached_array:
            array = self._attached_array
            attrs['array'] = array.tag
            if array.threshold is not None:
                attrs['threshold'] = array.threshold
            if array.offset is not None:
                attrs['offset'] = array.offset

        return attrs

    def getXml(self):
        elem = etree.Element('axis')
        for attr, val in iteritems(self.getXmlAttrs()):
            elem.set(attr, str(val))
        return elem


class HistogramConfBank(HistogramConfElement):
    """ The Bank configuration element of the XML file. The bank has
    it's associated id which is to be used when fetching data from
    this bank. The bank can also have several axes attached. The rank
    of the bank (number of dimensions of the bank) is deduced from the
    number of axes attached to this bank.
    """
    parameters = {
        'bankid': Param('Integer id of the bank', type=int, mandatory=True)
    }

    attached_devices = {
        'axes': Attach('Axis for this bank', HistogramConfAxis, multiple=True)
    }

    @property
    def arrays(self):
        """ Provides a set of of all the arrays that appear in this
        bank.
        """
        # Collect all the arrays that occur in axis
        return set([ax._attached_array for ax in self.axes
                    if ax._attached_array])

    @property
    def axes(self):
        return self._attached_axes

    @property
    def shape(self):
        return [ax.length for ax in self.axes]

    def getXml(self):
        elem = etree.Element('bank', rank=str(len(self.axes)))
        for ax in self.axes:
            elem.append(ax.getXml())
        return elem


class ConfiguratorBase(HistogramConfElement):
    """ The SINQ histogram memory server is configured via an XML
    file containing configuration instructions. When the histogram
    memory has to be configured dynamically from the instrument
    control computer, http–POST request has to be sent to:
    <baseurl>/configure.egi with the content of the new configuration
    as XML in the body.

    The parameters in this class provide basic information about the HM
    using:
    *filler* (filler algorithm is used to do the actual histogramming),
    *hdr_daq_mask* (mask with which the headers of the data packets on the
    fibre optic link are anded),
    *hdr_daq_active* (the value which the headers of the data packest anded
    with hdr daq mask must have in order to be considered a valid packet
    suitable for histogramming.
    These two attributes allow to histogram only when all veto flags are OK.

    These parameters are written as attributes of the <sinqhm> top level
    xml element in the configuration file.

    This <sinqhm> element can have following children:
    *bank*: The memory can split into different banks and each of these banks
    has a rank and the description of corresponding axis.
    *array*: The axes in the banks can have corresponding arrays for tof
    and lookup axis types and are stored as separate entities within the
    XML file. The tag names must be those specified in the array attribute
    of the axis tag.

    Example of the sample configuration file:
    <?xml version="1.0" encoding="UTF-8"?>
    <sinqhm filler="tof" hdr_daq_mask=’’0x000000’’ hdr_daq_active=’’0x000000’’>
        <bank rank="2">
            <axis length="400" mapping="direct"/>
            <axis length="1000" mapping="boundary" array="tof"/>
        </bank>
        <tof rank="1" dim="1001">
            1000 2000 3000 4000 5000 6000 7000 8000 9000
            10000 11000 12000 13000 14000 15000 16000 17000 18000 19000
            ............. many numbers cut here ....................
        </tof>
    </sinqhm>
    """
    parameters = {
        'filler': Param('Filler algorithm to be used',
                        type=oneof('dig', 'tof', 'tofmap', 'psd', 'hrpt')),
        'mask': Param('Mask anded to the data packets on fiber optics',
                      type=str, default='0x000000'),
        'active': Param('The must have value for the packets anded with mask',
                        type=str, default='0x000000'),
        'increment': Param('The increment value', type=int, default=1)
    }

    attached_devices = {
        'banks': Attach('Banks attached to the histogram memory',
                        HistogramConfBank, multiple=True),
        'connector': Attach('HTTP Connector for Histogram Memory Server',
                            HttpConnector),
    }

    @property
    def arrays(self):
        """ The array elements of that should appear in the XML
        configuration file
        """
        # Collect all the arrays that occur in banks
        arrs = set()  # Store only the unique arrays in a set
        for bank in self.banks:
            if bank.arrays:
                arrs = arrs.union(bank.arrays)
        return arrs

    @property
    def banks(self):
        return self._attached_banks

    def getXml(self):
        elem = etree.Element('sinqhm', filler=self.filler,
                             hdr_daq_mask=self.mask,
                             hdr_daq_active=self.active,
                             increment=str(self.increment))
        for bank in self.banks:
            elem.append(bank.getXml())
        for array in self.arrays:
            elem.append(array.getXml())
        return elem

    def updateConfig(self):
        """ Generate a new configuration XML file and send it to the server
        """
        xmldata = self.getXmlString(encoding='UTF-8', xml_declaration=True,
                                    pretty_print=True)
        req = self._attached_connector.post('configure.egi', data=xmldata)
        self.log.info(req.text)
