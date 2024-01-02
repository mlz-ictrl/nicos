#!/usr/bin/env python3
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
A tool to copy NICOS cache to InfluxDB2 instance.
Usage: influxdb-cache-transfer.py -h
"""

import argparse
import ast
from datetime import datetime
import math
import multiprocessing
import os
import socket
import sys
import time
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from influxdb_client import InfluxDBClient, BucketRetentionRules, Point
from influxdb_client.client.write_api import SYNCHRONOUS as write_option
from numpy import arange
import requests

from nicos.utils.credentials.keystore import nicoskeystore


DB = None
LOG = None


class InfluxDB:
    """
    InfluxDB-client wrapper for cache copy procedure.
    """

    def __init__(self, url, keystoretoken, org):
        self._org = org
        self._bucket = None
        try:
            response = requests.head(url)
            if response.status_code != 200:
                raise OSError('Could not connect to the database.')
        except requests.exceptions.RequestException:
            raise OSError('Could not connect to the database.')
        self._token = nicoskeystore.getCredential(keystoretoken)
        if not self._token:
            raise OSError('InfluxDB API token missing in keyring')
        self._client = InfluxDBClient(url=url, token=self._token, org=org,
                                      timeout=30_000)
        self._write_api = self._client.write_api(write_options=write_option)

    def __del__(self):
        if self._client:
            self._client.close()

    def getBucketNames(self):
        db_names = []
        bucket_api = self._client.buckets_api()
        dbs = bucket_api.find_buckets().buckets
        for each in dbs:
            db_names.append(each.name)
        return db_names

    def addNewBucket(self, name):
        self._bucket = name
        if name not in self.getBucketNames():
            bucket_api = self._client.buckets_api()
            retention_rules = BucketRetentionRules(type='expire',
                                                   every_seconds=0)
            bucket_api.create_bucket(bucket_name=name,
                                     retention_rules=retention_rules,
                                     org=self._org)

    def writeTable(self, points):
        self._write_api.write(bucket=self._bucket, record=points)

    def read(self, bucket, measurement, field):
        msg = f'''from(bucket:"{bucket}")
            |> range(start: 2007-01-01T00:00:00Z, stop: now())
            |> filter(fn:(r) => r._measurement == "{measurement}")
            |> filter(fn:(r) => r._field == "{field}")
            |> drop(columns: ["_start", "_stop", "_time"])'''
        tables = self._client.query_api().query(msg)
        return tables

    def read_keys(self, bucket, tsfrom=None, tsto=None, measurement=None):
        fromtime = datetime.utcfromtimestamp(tsfrom).strftime("%Y-%m-%dT%H:%M:%SZ") \
            if tsfrom else '2007-01-01T00:00:00Z'
        totime = datetime.utcfromtimestamp(tsto).strftime("%Y-%m-%dT%H:%M:%SZ") \
            if tsto else 'now()'
        msg = 'import "influxdata/influxdb/schema"\n'
        if measurement:
            msg += f'schema.measurementFieldKeys(' \
               f'bucket: "{bucket}", measurement: "{measurement}", '
        else:
            msg += f'schema.measurements(bucket: "{bucket}", '
        msg += f'start: {fromtime}, stop: {totime})'
        tables = self._client.query_api().query(msg)
        keys = []
        for record in tables[0].records:
            keys.append(record['_value'])
        return sorted(keys)

    def count(self, bucket, measurement):
        msg = f"""
            from(bucket: "{bucket}")
            |> range(start: 2007-01-01T00:00:00Z, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            |> drop(columns: ["_start", "_stop"])
            |> count()
        """
        tables = self._client.query_api().query(msg)
        return tables


class TransferLog(InfluxDB):
    """
    Class to save progress of copying cache to InfluxDB.
    """

    def __init__(self, url, keystoretoken, org, bucket):
        super().__init__(url, keystoretoken, org)
        self._bucket = bucket
        self.addNewBucket(self._bucket)
        self._processed = []

    def add_entry(self, measurement, entries):
        point = Point(measurement)
        for entry in entries:
            for key, value in entry.items():
                point.field(key, value)
        self.writeTable(point)

    def read_processed(self, measurement, field):
        self._processed = []
        for table in self.read(self._bucket, measurement, field):
            for record in table.records:
                self._processed.append(record['_value'])
        return self._processed

    def is_processed(self, entry):
        return entry in self._processed

    def count_entry(self, measurement):
        count = 0
        for table in self.count(self._bucket, measurement):
            for record in table.records:
                count += record['_value']
        return count



def read_cache(cachePath):
    """
    Tool to return sorted list of cache files.

    Args:
        cachePath: absolute path to the cache file

    Returns: sorted list of cache files
    """

    if not os.path.exists(cachePath):
        raise OSError('Please add a valid path to the nicos-cache location.')
    excluded = ['.DS_Store', '.bak', '#']
    filelist = []
    count = 0
    for entry in sorted(os.listdir(cachePath)):
        try:
            _ = int(entry)
            for root, _, filenames in sorted(os.walk(os.path.join(cachePath, entry))):
                for filename in sorted(filenames):
                    if True not in [key in filename for key in excluded]:
                        filelist.append(os.path.join(root, filename))
                        count += 1
                    if count % 1000 == 0:
                        print(f'\x1b[KIndexing nicos files {count}\x1b[0F')
        except:
            continue
    return filelist


def parseFile(measurement, cachefile):
    """
    Parses individual cache file and prepares a table with values, that will
    be uploaded to InfluxDB.

    Args:
        measurement: accepts filename of a cache file, e.g. nicos-_lastconfig_
        cachefile: absolute path to the cache file

    Returns: list of InfluxDB Points
    """

    points, errorlog = [], []
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
                    errorlog.append(line)
                    continue
                expired = expired == "-"
                skip_keys = ['', '-']
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
                        value_float = list(value_float)[0] if len(value_float) == 1 and \
                            type(list(value_float)[0]) not in [list, tuple, set, dict] \
                            else None
                    if isinstance(value_float, int):
                        value_float = float(value_float)
                    if isinstance(value_float, float):
                        point = Point(measurement).time(ts)\
                            .field(f'{field}_float', value_float)\
                            .tag('expired', expired)
                        points.append(point)
                    point = Point(measurement).time(ts)\
                        .field(f'{field}', value)\
                        .tag('expired', expired)
                    points.append(point)
    return points, errorlog


def copyfile(influxUrl, cachefile, progress):
    """
    Copies single nicos cache file to InfulxDB and logs the process.

    Args:
        influxUrl: Url to InfluxDB instance
        cachefile: absolute path to the nicos cache file
        progress: ratio of processed nicos cache files to their total amount
    """

    print(f'\x1b[KProgress {format(progress, ".2f")}% {cachefile}\x1b[0F')
    global DB
    if DB is None:
        DB = InfluxDB(influxUrl, 'influxdb', 'mlz')
        DB.addNewBucket('nicos-cache')
    global LOG
    if LOG is None:
        LOG = TransferLog(influxUrl, 'influxdb', 'mlz', 'cache-transfer-log')
        LOG.read_processed('processed', 'filename')

    if not LOG.is_processed(cachefile):
        points, errorlog = parseFile(os.path.basename(cachefile), cachefile)
        for error in errorlog:
            LOG.add_entry('parse_errors', [{cachefile: error}])
        try:
            DB.writeTable(points)
            LOG.add_entry('processed', [{'filename': cachefile}])
        except Exception as e:
            LOG.add_entry('fault_files', [{cachefile: e}])
    return


def copy(influxUrl, cachePath):
    """
    Tool to copy flat file cache to InfluxDB.

    Args:
        influxUrl: Url to InfluxDB instance
        cachePath: Absolute file path to nicos flat file cache

    Returns: numbers of copied files
    """

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    filelist = read_cache(cachePath)
    progress, filescount = 0, len(filelist)
    for cachefile in filelist:
        progress += 1
        pool.apply_async(copyfile, (influxUrl, cachefile,
                                    progress / filescount * 100,))
    pool.close()
    pool.join()
    print()
    return filescount


def read_copy_errors(influxUrl):
    """
    Outputs from the InfluxDB all the errors related to copying process.

    Args:
        influxUrl: Url to InfluxDB instance
    """

    db = TransferLog(influxUrl, 'influxdb', 'mlz', 'cache-transfer-log')

    not_processed_files = db.read_keys('cache-transfer-log', measurement='fault_files')
    entries = {}
    for filename in not_processed_files:
        entries[filename] = db.read_processed('fault_files', filename)
    if entries:
        print(f'\nThere were {len(not_processed_files)} files not copied.')
        for filename, errors in entries.items():
            print(filename)
            for error in errors:
                print('\t', error)

    fault_entries_files = db.read_keys('cache-transfer-log', measurement='parse_errors')
    entries = {}
    for filename in fault_entries_files:
        entries[filename] = db.read_processed('parse_errors', filename)
    if entries:
        print(f'\nThere were {len(fault_entries_files)} corrupted entries.')
        for filename, errors in entries.items():
            print(filename)
            for error in errors:
                print('\t', error)


def query_cache(cache, port, msg):
    """
    Connects to nicos cache service and collects entries.

    Args:
        cache: address of the nicos cache
        port: port where nicos cache is bound
        msg: query message to nicos cache

    Returns: list of entries from nicos cache service
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((cache, port))
    client.settimeout(30)
    client.sendall(msg)
    res = b''
    while True:
        try:
            data = client.recv(1024)
        except (socket.timeout, ConnectionResetError):
            break
        res += data
        if b'###!' in data:
            break
    client.close()
    res = res.decode()
    res = res[:res.find('###!')]
    return res.split('\n')


def compare_cache_entries(key, cache1, cache2, fromTS=None, toTS=None,
                          interval=86400, batch=False, processed=None):
    """
    Compares entries between two nicos cache services.
    It is assumed that 1st cache is bound to 14869 port, whereas 2nd - to 14870.
    Outputs day by day comparison of entries obtained from both cache services.
    For debugging purposes, when interval is shorter than 60s, outputs are
    printed for user to compare.

    Args:
        key: nicos key/subkey pair, e.g. reactorpower/value
        cache1: address of 1st nicos cache, the port is assumed at 14869
        cache2: address of 2nd nicos cache, the port is assumed at 14870
        fromTS: timestamp of the beginning of the interested time range
        toTS: timestamp of the end of the interested time range
        interval: time interval to compare, default is 86400, i.e. 24h
        batch: True when used by automation tool, suppresses print outputs
        processed: list of processed entries

    Yields: timestamp and bool value if a day matches between DBs if batched,
    otherwise prints to standard output if time intervals match.
    """

    start = float(fromTS) if fromTS else datetime(2007, 1, 1).timestamp()
    stop = float(toTS) if toTS else datetime.now().timestamp()
    delta = float(interval)
    key = 'nicos/' + key if 'nicos/' not in key else key
    for ts in arange(start, stop, delta):
        ts = round(ts)
        if batch and processed:
            if round(ts) in processed:
                yield ts, None
                continue
        msg = f'{ts}-{ts + delta}@{key}?{None}\n###?\n'
        msg = msg.encode()

        # Querying InfluxDB
        output1 = query_cache(cache1, 14869, msg)
        # Creates dict of timestamps and values. InfluxDB and FlatfileDB
        # return timestamps with different precision, for that TSs
        # are rounded before stored
        table1 = {}
        for entry in output1:
            ts_pos = entry.find('@')
            value_pos = entry.find(key) + len(key) + 1
            if ts_pos != -1 and value_pos != -1:
                table1[round(float(entry[:ts_pos]), 6)] = entry[value_pos:]

        # Querying FlatfileDB
        output2 = query_cache(cache2, 14870, msg)
        # Parsing FlatfileDB output to get rid of empty and repeated values
        table2 = {}
        last_entry = ''
        for entry in output2:
            ts_pos = entry.find('@')
            value_pos = entry.find(key) + len(key) + 1
            if ts_pos != -1 and value_pos != -1:
                if entry[value_pos:] and float(entry[:ts_pos]) >= ts and \
                        float(entry[:ts_pos]) < ts + delta and entry != last_entry:
                    table2[round(float(entry[:ts_pos]), 6)] = entry[value_pos:]
                    last_entry = entry

        # Compare outputs from both DBs
        if batch:
            yield ts, table1 == table2
        else:
            print(datetime.utcfromtimestamp(ts),
                  'Ok' if table1 == table2 else f'Not ok {ts} {ts + delta}')
            if table1 != table2 and delta <= 60:
                print('InfluxDB values:\n', table1)
                print('FlatfileDB values:\n', table2)
                print()

    if not batch:
        yield


def compare_onekey(influxUrl, key, tsfrom, tsto, cache1, cache2):
    """
    Tool to compare entries for a single key/subkey.

    Args:
        influxUrl: Url to InfluxDB instance
        key: nicos key/subkey
        tsfrom: timestamp of the beginning of the interested time range
        tsto: timestamp of the end of the interested time range
        cache1: address of 1st nicos cache, the port is assumed at 14869
        cache2: address of 2nd nicos cache, the port is assumed at 14870
    """

    log = TransferLog(influxUrl, 'influxdb', 'mlz', 'compare-log')
    processed = log.read_processed('processed', key) + \
                log.read_processed('errored_days', key)
    gen = compare_cache_entries(key, cache1, cache2, tsfrom, tsto,
                                86400, True, processed)
    for ts, match in gen:
        if match:
            log.add_entry('processed', [{key: round(ts)}])
        elif match is not None:
            log.add_entry('errored_days', [{key: round(ts)}])


def compare_progress(influxUrl, total_entries):
    """
    Runs in a separate process, checks with InfluxDB and outputs to the standard
    output the status of comparing process.

    Args:
        influxUrl: Url to InfluxDB instance
        total_entries: total number of checks
    """

    log = TransferLog(influxUrl, 'influxdb', 'mlz', 'compare-log')
    count, errors = 0, 0
    while count + errors < total_entries:
        count = log.count_entry('processed')
        errors = log.count_entry('errored_days')
        print('\x1b[KProgress '
              f'{format(count / total_entries * 100, ".2f")}% '
              f': {count} of {total_entries} entries. '
              f'Errors: {errors}\x1b[0F')
        time.sleep(5)
    print()
    return


def compare_all(influxUrl, cache1, cache2, tsfrom, tsto):
    """
    Automation tool to compare_cache_entries()

    Args:
        influxUrl: Url to InfluxDB instance
        cache1: address of 1st nicos cache, the port is assumed at 14869
        cache2: address of 2nd nicos cache, the port is assumed at 14870
        tsfrom: timestamp of the beginning of the interested time range
        tsto: timestamp of the end of the interested time range
    """

    tsfrom = float(tsfrom)
    tsto = float(tsto)

    # Creates dict with all keys/subkeys to have an idea how much work to do
    db = InfluxDB(influxUrl, 'influxdb', 'mlz')
    keys = db.read_keys('nicos-cache', tsfrom, tsto)
    table, key_count = {}, 0
    for key in keys:
        table[key] = []
        for subkey in db.read_keys('nicos-cache', tsfrom, tsto, key):
            if '_float' not in subkey:
                table[key].append(subkey)
        key_count += len(table[key])

    total_entries = math.ceil(key_count * (tsto - tsfrom) / 86400)
    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)
    pool.apply_async(compare_progress, (influxUrl, total_entries,))
    for key, subkeys in table.items():
        for subkey in subkeys:
            pool.apply_async(compare_onekey, (influxUrl, f'{key}/{subkey}',
                                              tsfrom, tsto, cache1, cache2,))
    pool.close()
    pool.join()


def read_compare_errors(influxUrl):
    """
    Outputs from the InfluxDB all the errors related to comparing process.

    Args:
        influxUrl: Url to InfluxDB instance
    """

    db = TransferLog(influxUrl, 'influxdb', 'mlz', 'compare-log')
    keys = db.read_keys('compare-log', measurement='errored_days')
    entries = {}
    for key in keys:
        entries[key] = db.read_processed('errored_days', key)
    if entries:
        for key, timestamps in entries.items():
            for ts in timestamps:
                print(key, ts, ts + 86400)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
        'Copy nicos cache to InfluxDB 2.0 tool.')
    subparsers = parser.add_subparsers(dest='command')
    copy_parser = subparsers.add_parser('copy', help=
        'Copy cache, see copy -h')
    copy_parser.add_argument('influxUrl', help='The URL to InfluxDB instance')
    copy_parser.add_argument('cachePath', help='The local path to nicos cache')

    readErrors_parser = subparsers.add_parser('read-copy-errors', help=
        'Read copying log, see read-copy-errors -h')
    readErrors_parser.add_argument('influxUrl', help=
        'The URL to InfluxDB instance.')

    compare_parser = subparsers.add_parser('compare-cache-entries', help=
        'Compare values from 2 nicos caches, see compare-cache-entries -h')
    compare_parser.add_argument('cache1', help='Address of 1st nicos-cache, '
                                               'assumed the port is 14869')
    compare_parser.add_argument('cache2', help='Address of 2nd nicos-cache '
                                               'assumed the port is 14870')
    compare_parser.add_argument('category', help='The key/subkey to compare')
    compare_parser.add_argument('fromTS', help='Timestamp to start from')
    compare_parser.add_argument('toTS', help='Timestamp to stop at')
    compare_parser.add_argument('interval', help='Time interval to compare')

    compareAll = subparsers.add_parser('compare-all', help=
        'Automated tool to compare all available cache entries, '
        'see compare-all -h')
    compareAll.add_argument('influxUrl', help='The URL to InfluxDB instance')
    compareAll.add_argument('cache1', help='Address of 1st nicos-cache, '
                                           'assumed the port is 14869')
    compareAll.add_argument('cache2', help='Address of 2nd nicos-cache '
                                           'assumed the port is 14870')
    compareAll.add_argument('tsfrom', help='Timestamp to start from')
    compareAll.add_argument('tsto', help='Timestamp to stop at')

    readCompare_parser = subparsers.add_parser('read-compare-errors', help=
        'Read compare log, see read-compare-errors -h')
    readCompare_parser.add_argument('influxUrl', help=
        'The URL to InfluxDB instance.')

    args = parser.parse_args()

    if args.command == 'copy':
        files = copy(args.influxUrl, args.cachePath)
        print(f'Copied {files} cache files.')
        read_copy_errors(args.influxUrl)
    elif args.command == 'read-copy-errors':
        read_copy_errors(args.influxUrl)
    elif args.command == 'compare-cache-entries':
        # compare_cache_entries is a generator function, but not necessarily
        # yields data
        next(compare_cache_entries(args.category, args.cache1, args.cache2,
                                   args.fromTS, args.toTS, args.interval))
    elif args.command == 'compare-all':
        compare_all(args.influxUrl, args.cache1, args.cache2,
                    args.tsfrom, args.tsto)
        read_compare_errors(args.influxUrl)
    elif args.command == 'read-compare-errors':
        read_compare_errors(args.influxUrl)
    else:
        print(f"Invalid command: {args.command}")
