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
#   Matt Clarke <matt.clarke@esss.se>
#
# *****************************************************************************
from nicos import session
from nicos.commands import usercommand, parallel_safe
from nicos.core.constants import SIMULATION
import json
import time
import datetime
from kafka import KafkaProducer, KafkaConsumer, TopicPartition


FW_CONFIG_FILE = "/home/nicos/ymir_filewriter_config.json"
JOB_ID = "62075348-cfe5-11e9-9141-c8f75089fb03"
BROKER = "172.30.242.20:9092"
COMMAND_TOPIC = "UTGARD_writerCommand"
RUNINFO_TOPIC = 'UTGARD_runInfo'
FILENUMBER_TOPIC ='nicos_filenumber'
INSTRUMENT_NAME = "YMIR"

@usercommand
@parallel_safe
def start_filewriter(title="No title"):
    """
    A hacky way of starting the NeXus Filewriter.
    """
    if session.mode == SIMULATION:
        session.log.info('=> dry run: starting file writing')
    else:
        iso8601_time = datetime.datetime.utcnow().isoformat().split(".")[0]
        starttime = int(time.time() * 1000)
        starttime_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(starttime / 1000))
        with open(FW_CONFIG_FILE, "r") as f:
            command_str = f.read()
        command_str = command_str.replace("STARTTIME", str(starttime))
        command_str = command_str.replace("8601TIME", iso8601_time)
        command_str = command_str.replace("TITLE", title)
        command = json.loads(command_str)

        file_id = get_file_number(update=True)
        # Set the values that can be different between runs
        command["file_attributes"] = {
            "file_name": file_id.zfill(8) + ".hdf"
        }

        command["job_id"] = file_id
        command["broker"] = BROKER
        command["start_time"] = starttime

        session.log.info('Started file writing job %s at: %s (%s)',
                      str(file_id), starttime_str, starttime)
        session.log.info(command["file_attributes"]["file_name"])

        send_to_kafka(COMMAND_TOPIC, json.dumps(command).encode())


@usercommand
@parallel_safe
def stop_filewriter(job_id=None):
    """
    A hacky way of stopping the NeXus Filewriter.
    """
    if session.mode == SIMULATION:
        session.log.info('=> dry run: stopping file writing')
    else:
        stoptime = int(time.time() * 1000)

        command = {
            "cmd": "FileWriter_stop",
            "job_id": get_file_number() if not job_id else str(job_id),
            "stop_time": stoptime
        }

        session.log.info('Stopped file writing at: %s', stoptime)
        send_to_kafka(COMMAND_TOPIC, json.dumps(command).encode())


def send_to_kafka(topic, message):
    producer = KafkaProducer(bootstrap_servers=BROKER, max_request_size=100000000)
    producer.send(topic, bytes(message))
    producer.flush()


def get_file_number(update=False):
    consumer = KafkaConsumer(bootstrap_servers=BROKER)
    tp = TopicPartition(FILENUMBER_TOPIC, 0)

    # Get last value
    consumer.assign([tp])
    consumer.seek_to_end(tp)
    pos = consumer.position(tp)
    if pos > 0:
        consumer.seek(tp, pos - 1)

        data = []
        while not data:
            data = consumer.poll(5)
        curr = int(data[tp][-1].value)
    else:
        curr = 1

    if update:
        curr += 1
        send_to_kafka(FILENUMBER_TOPIC, str(curr).encode())
    return str(curr)

