#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

"""
A tool to transfer NICOS cache to InfluxDB2 instance.
Usage:
influx-transfer-cache.py /path_to_cache
"""

import os
import sys
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from datetime import datetime
import ast

from influxdb_client import InfluxDBClient, BucketRetentionRules, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

from nicos.utils.credentials.keystore import nicoskeystore


class InfluxDB:
    def __init__(self, url, token, org):
        self._url = url
        self._token = token
        self._org = org
        self._client = InfluxDBClient(url=self._url, token=self._token,
                                      org=self._org)

    def __del__(self):
        self._client.close()

    def getBucketNames(self):
        db_names = []
        try:
            bucket_api = self._client.buckets_api()
            dbs = bucket_api.find_buckets().buckets
        except Exception as e:
            raise e
        for each in dbs:
            db_names.append(each.name)
        return db_names

    def addNewBucket(self, name):
        if name not in self.getBucketNames():
            try:
                bucket_api = self._client.buckets_api()
                retention_rules = BucketRetentionRules(type='expire',
                                                       every_seconds=0)
                bucket_api.create_bucket(bucket_name=name,
                                         retention_rules=retention_rules,
                                         org=self._org)
            except Exception as e:
                raise e

    def writeTable(self, bucket, points):
        try:
            write_api = self._client.write_api(write_options=ASYNCHRONOUS)
            write_api.write(bucket=bucket, record=points)
        except Exception as e:
            raise e

    def read(self, bucket, measurement, field):
        msg = f'from(bucket:"{bucket}")'
        # quering without time interval is not documented in influxdb_client
        # then 10y should suffice
        msg += '|> range(start: -10y)'
        msg += f'|> filter(fn:(r) => r._measurement == "{measurement}")'
        msg += f'|> filter(fn:(r) => r._field == "{field}")'
        msg += '|> drop(columns: ["_start", "_stop"])'
        tables = self._client.query_api().query(msg)
        return tables


def parseFile(measurement, cachefile, log):
    points = []
    measurement = measurement.replace('-', '/') #category
    with open(cachefile, 'r') as file:
        line = file.readline()
        while line:
            line = file.readline()
            if line != '':
                try:
                    #subkey, time, hasttl, value
                    field, ts, expired, value = line[:len(line)-1].split('\t')
                except Exception as e:
                    log.add_parseerror(cachefile, line)
                    continue
                expired = expired == "-"
                skip_keys = ['', '-', 'None', '{}', '()', '[]']
                if value and value not in skip_keys:
                    try:
                        ts = datetime.utcfromtimestamp(float(ts))
                    except:
                        continue
                    try:
                        value_float = ast.literal_eval(value)
                    except:
                        value_float = None
                    if type(value_float) in [list, tuple, set]:
                        value = list(value_float)[0] if len(value_float) == 1 and \
                            type(list(value_float)[0]) not in [list, tuple, set, dict] \
                            else str(value_float)
                    if type(value_float) == int:
                        value_float = float(value_float)
                    if type(value_float) == float:
                        point = Point(measurement).time(ts)\
                            .field(f'{field}_float', value_float)\
                            .tag('expired', expired)
                        points.append(point)
                    point = Point(measurement).time(ts)\
                        .field(f'{field}', value)\
                        .tag('expired', expired)
                    points.append(point)
    return points


class TransferLog(InfluxDB):
    def __init__(self, url, token, org):
        super().__init__(url, token, org)
        self._bucket = 'cache-transfer-log'
        self.addNewBucket(self._bucket)
        self._processed = self.read_precessed('filenames')

    def read_precessed(self, log):
        result = []
        tables = self.read(self._bucket, log, 'filename')
        for table in tables:
            for record in table.records:
                result.append(record['_value'])
        return result

    def add_processed(self, filename):
        self._processed.append(filename)
        point = Point('filenames').field('filename', filename)
        self.writeTable(self._bucket, point)

    def add_errored(self, filename, error):
        point = Point('fault_files').field('filename', filename)\
            .field('error', str(error))
        self.writeTable(self._bucket, point)

    def add_parseerror(self, filename, line):
        point = Point('parse_errors').field('filename', filename)\
            .field('error', line)
        self.writeTable(self._bucket, point)

    def is_processed(self, filename):
        return filename in self._processed


def main():
    url = 'http://localhost:8086'
    keystoretoken = 'influxdb'
    org = 'mlz'
    token = nicoskeystore.getCredential(keystoretoken)
    if not token:
        raise OSError('InfluxDB API token missing in keyring')
    db = InfluxDB(url, token, org)
    log = TransferLog(url, token, org)

    bucket = 'nicos-cache'
    db.addNewBucket(bucket)

    path = sys.argv[1]
    years = []
    for entry in os.listdir(path):
        try:
            value = int(entry)
        except:
            value = None
        if value:
            years.append(entry)

    excluded = ['.DS_Store']
    for year in years:
        for root, _, filenames in os.walk(path + year):
            for filename in filenames:
                if filename not in excluded:
                    cachefile = os.path.join(root, filename)
                    if not log.is_processed(cachefile):
                        print(cachefile)
                        points = parseFile(filename, cachefile, log)
                        try:
                            db.writeTable(bucket, points)
                            log.add_processed(cachefile)
                        except Exception as e:
                            log.add_errored(cachefile, e)
    print('done')


if __name__ == '__main__':
    main()
