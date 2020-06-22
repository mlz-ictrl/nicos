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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.core import ConfigurationError, NicosError
from nicos.pycompat import iteritems, string_types

from nicos_ess.nexus.placeholder import DeviceValuePlaceholder, PlaceholderBase


class NexusElementBase(object):
    """ Interface class to define nexus elements. All NeXus elements define
    a method which represents the dict of this element.
    """

    def structure(self, name, metainfo):
        """ Provides the JSON for current element in NeXus structure
        :param name: Name of the element
        :param metainfo: metainfo from *dataset*
        :return: list of dict of the NeXus structure
        """
        raise NotImplementedError()


class NXAttribute(NexusElementBase):
    """ Class to represent NeXus Attribute
    """

    def __init__(self, value, dtype=None):
        self.value = value
        self.dtype = dtype

    def structure(self, name, metainfo):
        # Return the name and current value if value is not None

        # If the value is a placeholder then get the value from this
        # placeholder
        if isinstance(self.value, PlaceholderBase):
            info = self.value.fetch_info(metainfo)
            if not info:
                session.log.warning('Unable to fetch info for placeholder'
                                    ' %s', self.value)
                return {}
            self.value = info[0]

        # The value now should be of desired numeric/string type.
        if self.value is None:
            return {}

        return [{name: self.value}]


class NXDataset(NexusElementBase):
    """ Class to represent NeXus Datasets. Each dataset can have
    a data type and additional attributes.
    """

    def __init__(self, value, dtype=None, **attr):
        self.value = value
        self.dtype = dtype
        self.attrs = {}
        for key, val in iteritems(attr):
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val)
            self.attrs[key] = val

    def structure(self, name, metainfo):
        # If the value is a placeholder then get the details from this
        # placeholder
        if isinstance(self.value, PlaceholderBase):
            info = self.value.fetch_info(metainfo)
            if not info:
                session.log.warning('Unable to fetch info for placeholder'
                                    ' %s', self.value)
                return {}

            # Set the value and the unit from the info string
            self.value = info[0]
            if info[2]:
                # Write the units attribute
                self.attrs["units"] = NXAttribute(info[2])

        # Return nothing if value is None
        if self.value is None:
            return {}

        root_dict = {
            "type": "dataset",
            "name": name,
            "values": self.value,
        }

        # For lists and strings type is required
        if not self.dtype:
            if isinstance(self.value, list) and self.value:
                if isinstance(self.value[0], int):
                    self.dtype = "int32"
                    if self.value[0].bit_length > 32:
                        self.dtype = "int64"
                elif isinstance(self.value[0], float):
                    self.dtype = "double"
                elif isinstance(self.value[0], string_types):
                    self.dtype = "string"

            if isinstance(self.value, string_types):
                self.dtype = 'string'

        # Add the 'dtype' if specified
        root_dict['dataset'] = {}
        if self.dtype:
            root_dict['dataset']["type"] = self.dtype

            # If the type is string/list then the size is to be written
            if self.dtype == "string":
                root_dict['dataset']['string_size'] = len(self.value) + 1

        if isinstance(self.value, list):
            # Only 1D array supported by NICOS
            root_dict['dataset']['size'] = [len(self.value)]
        else:
            root_dict['dataset']['size'] = [1]

        # Add the attributes if present
        if self.attrs:
            attr_dict = {}
            for attr_name, attr in iteritems(self.attrs):
                # It is important to check if the type is of NXAttribute
                # Subclasses can directly change the self.attrs dict
                if isinstance(attr, NXAttribute):
                    for attr_structure in attr.structure(attr_name, metainfo):
                        if attr_structure:
                            attr_dict.update(attr_structure)

            root_dict["attributes"] = attr_dict

        return [root_dict]


class NXGroup(NexusElementBase):
    """ Class to represent NeXus Group. Each group has a class type and
    can additionally have children in the form of datasets and groups or
    can also have attributes associated.
    """

    def __init__(self, nxclass):
        self.nxclass = nxclass
        self.children = {}
        self.attrs = {}

    def structure(self, name, metainfo):
        val = {
            "type": "group",
            "name": name,
            "attributes": {
                "NX_class": self.nxclass
            },
            "children": []
        }

        # Add the children
        if self.children:
            for ename, entry in iteritems(self.children):
                if isinstance(entry, NexusElementBase):
                    for child_dict in entry.structure(ename, metainfo):
                        if child_dict:
                            val["children"].append(child_dict)
                else:
                    session.log.info("%s does not provide value!!", ename)

        # Add the attributes
        if self.attrs:
            attr_dict = {}
            for attr_name, attr in iteritems(self.attrs):
                # It is important to check if the type is of NXAttribute
                # Subclasses can directly change the self.attrs dict
                if isinstance(attr, NXAttribute):
                    for attr_structure in attr.structure(attr_name, metainfo):
                        if attr_structure:
                            attr_dict.update(attr_structure)

            val["attributes"].update(attr_dict)

        return [val]


class NXLink(NexusElementBase):
    """ Class to represent NeXus Group. Each group has a class type and
    can additionally have children in the form of datasets and groups or
    can also have attributes associated.
    """

    def __init__(self, target):
        self.target = target

    def structure(self, name, metainfo):
        return [{
            'type': 'link',
            'name': name,
            'target': self.target
        }]


class KafkaStream(NexusElementBase):
    """ Class to represent Kafka streams.
    The defined properties of the stream can be set. The FileWriter
    using these properties fills up the data in the files using messages
    from Kafka.
    """
    stream_keys = ['broker', 'topic', 'source', 'writer_module', 'type',
                   'array_size', 'store_latest_into']

    def __init__(self, **attr):
        self.stream = {}
        for key in self.stream_keys:
            self.stream[key] = None

        self.stream_attrs = {}
        for key, val in iteritems(attr):
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val)
            self.stream_attrs[key] = val

    def store_latest_into(self, dataset_name):
        """Stores the final/latest value of the stream into the
        dataset with name dataset_name
        """
        self.set('store_latest_into', dataset_name)

    def set(self, key, value):
        if key not in self.stream:
            session.log.error('Unidentified key %s set for kafka stream', key)
            return
        self.stream[key] = value

    def structure(self, name, metainfo):
        stream_dict = {
            "type": "stream",
            "stream": {k: v for k, v in iteritems(self.stream) if v}
        }

        # Add the attributes
        if self.stream_attrs:
            attr_dict = {}
            for attr_name, attr in iteritems(self.stream_attrs):
                if isinstance(attr, NXAttribute):
                    for attr_structure in attr.structure(attr_name, metainfo):
                        if attr_structure:
                            attr_dict.update(attr_structure)

            stream_dict["attributes"] = attr_dict
        return [stream_dict]


class CacheStream(DeviceValuePlaceholder, KafkaStream):
    """Streams NICOS cache data"""

    def __init__(self, device, dtype, separate_log=False,
                 parameter='value', **attr):
        KafkaStream.__init__(self, **attr)
        DeviceValuePlaceholder.__init__(self, device, parameter)
        self.set('type', dtype)
        self.set('writer_module', 'ns10')
        self.separate_log = separate_log

    def structure(self, name, metainfo):
        try:
            nx = session.getDevice('NexusDataSink')
        except ConfigurationError:
            session.log.warning("NexusDataSink not found!! Can't track device "
                                "%s..", self.device)
            return
        self.set('broker', nx.brokers[0])
        self.set('topic', nx.cachetopic)
        key = 'nicos/' + self.device + '/' + self.parameter
        self.set('source', key)

        # Add the attributes
        self.stream_attrs["nicos_name"] = NXAttribute(self.device)
        self.stream_attrs["nicos_param"] = NXAttribute(self.parameter)
        self.stream_attrs["source_name"] = NXAttribute(key)

        info = self.fetch_info(metainfo)
        if info:
            self.stream_attrs["units"] = NXAttribute(info[2])

        if self.separate_log:
            self.store_latest_into(name)
            gname = name + '_log'
        else:
            gname = name

        group_dict = NXGroup('NXlog').structure(gname, metainfo)[0]
        stream_dicts = KafkaStream.structure(self, name, metainfo)
        group_dict["children"] += stream_dicts

        struct = [group_dict]

        if self.separate_log:
            link = NXLink(gname + '/' + name).structure(name, metainfo)
            struct += link

        return struct


class DeviceStream(DeviceValuePlaceholder, KafkaStream):
    """ Streams device parameter using data of associated PVs present in
    the form of Kafka messages. Note, to use this the forwarder must be
    forwarding the PVs to the topics. Internally, PV names are fetched
    from the device and corresponding topic and schema data is fetched
    from the Forwarder Device.
    """

    def __init__(self, device, parameter='value', separate_log=True, **attr):
        KafkaStream.__init__(self, **attr)
        DeviceValuePlaceholder.__init__(self, device, parameter)
        self.separate_log = separate_log

    def structure(self, name, metainfo):
        device = session.getDevice(self.device)
        parameter = self.parameter

        if parameter == 'value':
            parameter = 'readpv'

        # Fetch the PV name for the parameter. This will fail if the
        # parameter name is not mapped to the PV in class
        source = device._get_pv_name(parameter)

        # Get the forwarded topic and schema for the PV
        try:
            forwarder = session.getDevice('KafkaForwarder')
        except ConfigurationError:
            session.log.warning("FORWARDER not found!! Can't track device "
                                "%s..", device.name)
            return

        if not forwarder.is_process_running():
            session.log.warning('Forwarder is not running. Correct values will'
                                ' not be written for device %s.', device.name)

        topicandschema = forwarder.pv_forwarding_info(source)
        if not topicandschema:
            raise NicosError('Info not found for device %s and its '
                             'property: %s' % (device.name, parameter))

        # Infer the type, count of PV
        dbr_type = device._pvs[parameter].type
        count = device._pvs[parameter].count
        if '_' in dbr_type:
            dbr_type = dbr_type.split('_')[-1]

        if count > 1:
            self.set('array_size', count)

        self.set('type', dbr_type)
        self.set('source', source)
        self.set('topic', topicandschema[0])
        self.set('writer_module', topicandschema[1])
        self.set('broker', forwarder.brokers[0])

        # Add the attributes
        self.stream_attrs["nicos_name"] = NXAttribute(self.device)
        self.stream_attrs["nicos_param"] = NXAttribute(self.parameter)
        self.stream_attrs["source_name"] = NXAttribute(source)

        info = self.fetch_info(metainfo)
        if info:
            self.stream_attrs["units"] = NXAttribute(info[2])

        if self.separate_log:
            self.store_latest_into(name)
            gname = name + '_log'
        else:
            gname = name

        group_dict = NXGroup('NXlog').structure(gname, metainfo)[0]
        stream_dicts = KafkaStream.structure(self, name, metainfo)
        group_dict["children"] += stream_dicts

        struct = [group_dict]

        if self.separate_log:
            link = NXLink(gname + '/' + name).structure(name, metainfo)
            struct += link

        return struct


class EventStream(KafkaStream):
    """ Stream that provides event data from Kafka
    """

    def __init__(self, topic, source, broker, mod='ev42', dtype='uint64',
                 **attr):
        KafkaStream.__init__(self, **attr)
        self.set('topic', topic)
        self.set('source', source)
        self.set('broker', broker)
        self.set('writer_module', mod)
        self.set('type', dtype)


class DeviceAttribute(NXAttribute):
    """ NeXus Attribute, the value of which comes from a *device*.
    The *parameter* to be fetched can be set, otherwise will fetch
    the value of the device. Optionally a data type can also be
    provided.
    """

    def __init__(self, device, parameter='value', dtype=None, defaultval=None):
        val = DeviceValuePlaceholder(device, parameter, defaultval)
        NXAttribute.__init__(self, val, dtype)


class DeviceDataset(NXDataset):
    """ NeXus Attribute, the value of which comes from a *device*.
    The *parameter* to be fetched can be set, otherwise will fetch
    the value of the device. Optionally a data type and attributes
    associated to this dataset can also be added.
    """

    def __init__(self, device, parameter='value', dtype=None, defaultval=None,
                 **attr):
        val = DeviceValuePlaceholder(device, parameter, defaultval)
        NXDataset.__init__(self, val, dtype, **attr)

        # Set the NICOS data as attributes
        if defaultval is not None:
            self.attrs["default_value"] = NXAttribute(defaultval)
        self.attrs["nicos_name"] = NXAttribute(device)
        self.attrs["nicos_param"] = NXAttribute(parameter)
