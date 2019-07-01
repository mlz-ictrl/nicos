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
#   Matt Clarke <matt.clarke@esss.se>
#
# *****************************************************************************
import json
import kafka
import numpy as np
import time
from nicos.core.device import Measurable
from nicos_ess.devices.kafka.consumer import KafkaSubscriber
import nicos_ess.devices.fbschemas.hs00.EventHistogram as EventHistogram
import nicos_ess.devices.fbschemas.hs00.ArrayDouble as ArrayDouble
from nicos_ess.devices.fbschemas.hs00.Array import Array
from nicos.core import ArrayDesc, Override, Param, status, tupleof, Value
from nicos.core.constants import LIVE


def get_schema(buf):
    """
    Extract the schema code embedded in the buffer

    :param buf: The raw buffer of the FlatBuffers message.
    :return: The schema name
    """
    return buf[4:8].decode("utf-8")


def deserialise_hs00(buf):
    """
    Convert flatbuffer into a histogram.

    :param buf:
    :return: dict of histogram information
    """
    # Check schema is correct
    schema = get_schema(buf)
    if schema != "hs00":
        raise Exception(
            "Incorrect schema: expected hs00 but got {}".format(schema))

    event_hist = EventHistogram.EventHistogram.GetRootAsEventHistogram(buf, 0)

    dims = []
    for i in range(event_hist.DimMetadataLength()):
        bins_fb = event_hist.DimMetadata(i).BinBoundaries()

        # Get bins
        temp = ArrayDouble.ArrayDouble()
        temp.Init(bins_fb.Bytes, bins_fb.Pos)
        bins = temp.ValueAsNumpy()

        # Get type
        if event_hist.DimMetadata(i).BinBoundariesType() == Array.ArrayDouble:
            bin_type = np.float64
        else:
            raise TypeError("Type of the bin boundaries is incorrect")

        hist_info = {
            "length": event_hist.DimMetadata(i).Length(),
            "edges": bins,
            "type": bin_type,
        }
        dims.append(hist_info)

    # Get the data
    if event_hist.DataType() != Array.ArrayDouble:
        raise TypeError("Type of the data array is incorrect")

    data_fb = event_hist.Data()
    temp = ArrayDouble.ArrayDouble()
    temp.Init(data_fb.Bytes, data_fb.Pos)
    data = temp.ValueAsNumpy()
    shape = event_hist.CurrentShapeAsNumpy().tolist()

    hist = {
        "source": event_hist.Source().decode("utf-8"),
        "shape": shape,
        "dims": dims,
        "data": data.reshape(shape),
        "info": event_hist.Info().decode("utf-8")
        if event_hist.Info()
        else "",
    }
    return hist


class JustBinItDetector(KafkaSubscriber, Measurable):
    parameters = {
        'hist_topic': Param('The topic to listen on for the histogram data',
                            type=str, userparam=False, settable=False,
                            mandatory=True),
        'data_topic': Param('The topic to listen on for the event data',
                            type=str, userparam=False, settable=False,
                            mandatory=True),
        'command_topic': Param('The topic to send just-bin-it commands to',
                               type=str, userparam=False, settable=False,
                               mandatory=True),
        'tof_range': Param('The time-of-flight range to histogram',
                           type=tupleof(int, int),
                           default=(0, 100000000), userparam=True,
                           settable=True),
        'num_bins': Param('The number of bins to histogram into',
                          type=int,
                          default=50, userparam=True, settable=True),
        'curstatus': Param('Store the current device status',
                           internal=True, type=tupleof(int, str),
                           default=(status.OK, ""),
                           settable=True),
    }

    parameter_overrides = {
        'unit': Override(default='events', settable=False, mandatory=False),
    }

    def doPrepare(self):
        self.curstatus = status.BUSY, "Preparing"
        self._producer = kafka.KafkaProducer(bootstrap_servers=self.brokers)

        # Set up the consumer
        KafkaSubscriber.doPreinit(self, None)
        self.subscribe(self.hist_topic)
        self.curstatus = status.OK, ""

    def new_messages_callback(self, messages):
        # Only care about most recent message
        key = list(messages.keys())[-1]
        hist = deserialise_hs00(messages[key])
        info = json.loads(hist["info"])
        if info["state"] == "COUNTING":
            self.curstatus = status.BUSY, "Counting"
        else:
            self.curstatus = status.OK, ""

        self._hist_data = hist["data"]
        self._hist_edges = hist["dims"][0]["edges"]

    def doStart(self):
        self.curstatus = status.BUSY, "Starting"

        # Generate a unique-ish id
        unique_id = "nicos-{}".format(int(time.time()))
        config = self._create_config(self._count_secs, unique_id)

        # Ask just-bin-it to start counting
        self.log.info(
            "Starting counting for {} seconds".format(self._count_secs))
        self._send(self.command_topic, json.dumps(config).encode("utf-8"))

    def _send(self, topic, message):
        self._producer.send(topic, message)
        self._producer.flush()

    def _create_config(self, interval, identifier):
        return {
            "cmd": "config",
            "data_brokers": self.brokers,
            "data_topics": [self.data_topic],
            "interval": interval,
            "histograms": [
                {
                    "type": "hist1d",
                    "tof_range": list(self.tof_range),
                    "num_bins": self.num_bins,
                    "topic": self.hist_topic,
                    "id": identifier
                }
            ]
        }

    def doRead(self, maxage=0):
        return [sum(self._hist_data)]

    def doReadArrays(self, quality):
        return self._hist_data

    def doFinish(self):
        self._stop_processing()

    def _stop_processing(self):
        if self._updater_thread is not None:
            self._stoprequest = True
            if self._updater_thread.is_alive():
                self._updater_thread.join()
            self._consumer.close()
        self.curstatus = status.OK, ""

    def doSetPreset(self, t, **preset):
        self.curstatus = status.BUSY, "Preparing"
        self._hist_data = np.array([])
        self._hist_edges = np.array([])
        self._count_secs = t

    def doStop(self):
        # Treat like a finish
        self._stop_processing()

    def doStatus(self, maxage=0):
        return self.curstatus

    def duringMeasureHook(self, elapsed):
        return LIVE

    def valueInfo(self):
        return Value(self.name, unit=self.unit),

    def arrayInfo(self):
        return ArrayDesc('data', shape=(self.num_bins,),
                         dtype=np.float64),
