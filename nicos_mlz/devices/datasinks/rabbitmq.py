# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Moritz Hannemann <m.hannemann@fz-juelich.de>
#
# *****************************************************************************

import json
import os
import uuid
from datetime import datetime, timezone
from os import path

import pika

from nicos import session
from nicos.core import Override, Param
from nicos.core.constants import BLOCK, MASTER, POINT, SCAN, SUBSCAN
from nicos.core.data import BaseDataset, BlockDataset, DataSink, \
    DataSinkHandler, ScanDataset


def metainfo_to_json(metainfo):
    """Prepare metadata in suitable json format"""
    metadata = {}

    for (dev, parm), (value, _str_value, unit, category) in metainfo.items():
        metadata.setdefault(dev, {})
        metadata[dev][parm] = {
            'value': value,
            'unit': unit,
            'category': category
        }
    return metadata


def valuestats_to_json(valuestats):
    return {k: v._asdict() for k, v in valuestats.items()}


class Message:
    id: str  # pylint: disable=redefined-builtin
    event: str
    metadata: dict

    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        id: uuid.UUID,  # pylint: disable=redefined-builtin
        scanid: uuid.UUID,
        blockid: uuid.UUID,
        event: str,
        started: str,
        fileinfos: list,
        mapping: dict,
        metainfo: dict,
        statistics: dict,
    ):
        self.id = str(id)
        self.blockid = str(blockid) or None
        self.scanid = str(scanid) or None
        self.event = event
        self.creation_timestamp = started
        self.fileinfos = fileinfos
        self.mapping = mapping
        self.metadata = metainfo
        self.statistics = statistics

    def __str__(self):
        return json.dumps({**self.__dict__})


class RabbitSinkHandler(DataSinkHandler):

    ordering = 80

    def _handleMessage(self, event: str, dataset: BaseDataset,
                       scands: ScanDataset = None,
                       blockds: BlockDataset = None):
        """Prepare the data and send the metainfo, if available, and other
        information to the Queue"""
        started = (datetime.fromtimestamp(dataset.started, tz=timezone.utc)
                   .isoformat())

        metadata = {}
        if dataset.settype != BLOCK:
            metadata = metainfo_to_json(dataset.metainfo)
        msg = Message(
            id=dataset.uid,
            scanid=scands.uid if scands else None,
            blockid=blockds.uid if blockds else None,
            event=event,
            started=started,
            fileinfos=self._handleFileInfo(dataset),
            mapping={
                'experiment': session.experiment.name,
                'sample': session.experiment.sample.name,
                'instrument': session.instrument.name,
            },
            metainfo=metadata,
            statistics=valuestats_to_json(dataset.valuestats),
        )
        self.sink._sendMessage(msg)

    def _getScanDatasetParents(self, dataset):
        """Returns a tuple of `BlockDataset`, `ScanDataset` if available.

        get parent `ScanDataset` (subscan) and `BlockDataset` for this
        `ScanDataset` if available
        """
        scands, blockds = None, None
        for ds in self.manager.iterParents(dataset, settypes=(BLOCK, SCAN)):
            if ds.settype == BLOCK:
                blockds = ds
            elif ds.settype == SCAN:
                scands = ds
        return blockds, scands

    def _handleFileInfo(self, dataset):
        finfos = []
        for fname, fpath in zip(dataset.filenames, dataset.filepaths):
            stat = {}
            try:
                st = os.stat(fpath)
                stat['size']= st.st_size
                stat['atime'] = st.st_atime
                stat['mtime'] = st.st_mtime
                stat['ctime'] = st.st_ctime
                stat['mode'] = st.st_mode
                stat['uid'] = st.st_uid
                stat['gid'] = st.st_gid
                stat['inode'] = st.st_ino
            except OSError:
                # not all sinks really write the files, some do it
                # indirectly
                pass
            finfos.append({
                'name': fname,
                'path': fpath,
                'stat': stat,
                'samplepath': path.realpath(session.experiment.samplepath),
            })
        return finfos

    def addSubset(self, subset):
        # do not take into account addSubset of scans to blocks
        # this is handled in `end()`.
        if subset.settype != POINT:
            return
        blockds, scands = self._getScanDatasetParents(self.dataset)
        if subset.number == 1:  # begin of ScanDataset including metainfo
            self._handleMessage(self.dataset.settype, self.dataset, scands,
                                blockds)
        self._handleMessage(subset.settype, subset, self.dataset, blockds)

    def begin(self):
        self.log.debug("begin: dataset.settype = %s", self.dataset.settype)
        # need to skip begin of ScanDataset as metainfo is not available
        # before the first point. This is handled on the first point in
        # `addSubset`.
        if self.dataset.settype not in (SCAN, SUBSCAN):
            self._handleMessage(self.dataset.settype, self.dataset)

    def end(self):
        self.log.debug("end: dataset.settype = %s", self.dataset.settype)
        blockds, scands = None, None
        if self.dataset.settype in (SCAN, SUBSCAN):
            # the `ScanDataset` has been popped from DataManager's stack before
            # dispatching `finish`. Parents are left on the stack, using
            # `iter(self.manager._stack)` though.
            blockds, scands = self._getScanDatasetParents(None)
        self._handleMessage(f'{self.dataset.settype}.end', self.dataset,
                            scands, blockds)


class RabbitSink(DataSink):
    """Creates a RabbitMQ exchange and queue on the parameterized instance
    and writes all metainfo synchronously into it for further processing.
    """
    parameters = {
        'rabbit_url': Param('RabbitMQ server url', type=str, mandatory=True),
    }

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN, BLOCK])
    }

    handlerclass = RabbitSinkHandler
    _connection = None
    _channel = None

    def doInit(self, mode):
        if mode == MASTER:
            self._connect()
            self._prepareExchange()
            self._prepareQueue()

    def doShutdown(self):
        if self._connection is not None:
            self._connection.close()

    def _connect(self):
        """Connects to the RabbitMQ instance"""
        parameters = pika.URLParameters(self.rabbit_url)
        self._connection = pika.BlockingConnection(parameters=parameters)
        self._channel = self._connection.channel()

    def _prepareExchange(self):
        """Declares the Exchange on the RabbitMQ instance"""
        self._exchange = f'{session.instrument.instrument}'
        self._channel.exchange_declare(
            self._exchange,
            # exchange_type=ExchangeType.direct,
            durable=True,
            auto_delete=False)

    def _prepareQueue(self):
        """Declares the Queue and its bindings on the RabbitMQ instance"""
        self._queue = self._channel.queue_declare(
            f'{session.instrument.instrument}',
            exclusive=False,
            durable=True,
            auto_delete=False).method.queue

        self._channel.queue_bind(
            exchange=self._exchange,
            queue=self._queue,
            routing_key=session.instrument.instrument)

    def _sendMessage(self, msg):
        for retry in range(3):
            try:
                if retry > 0:  # reconnect
                    self._connect()
                self._channel.basic_publish(
                    exchange=self._exchange,
                    routing_key=session.instrument.instrument,
                    body=str(msg),
                    properties=pika.BasicProperties(
                        content_type='application/json'))
                break
            except (pika.exceptions.AMQPChannelError,
                    pika.exceptions.AMQPConnectionError) as e:
                self.log.debug('reconnect #%d due to %r', retry + 1, e)
                exc = e
        else:
            raise exc
