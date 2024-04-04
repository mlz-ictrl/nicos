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

import ast
import asyncio
import csv
import threading
from datetime import datetime

import influxdb_client
from influxdb_client import BucketRetentionRules, InfluxDBClient, Point

try:
    from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
except ImportError:
    pass
from influxdb_client.client.write_api import SYNCHRONOUS as write_option

from nicos.core import ConfigurationError, Param
from nicos.services.cache.database.base import CacheDatabase
from nicos.services.cache.entry import CacheEntry
from nicos.utils.credentials.keystore import nicoskeystore


csv.field_size_limit(0xA00000) # 10 MB limit for influx queries with big fields


class InfluxDBWrapper:
    """Wrapper for InfluxDB API 2.0.
    """

    def __init__(self, url, token, org, bucket, bucket_latest):
        self._update_queue = []
        self._update_lock = threading.Lock()
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket
        self._bucket_latest = bucket_latest
        self._client = InfluxDBClient(url=self._url, token=self._token,
                                      org=self._org, timeout=30_000)
        self._write_api = self._client.write_api(write_options=write_option)
        self.addNewBucket(self._bucket)

    def disconnect(self):
        self._update()
        self._client.close()

    def getBucketNames(self):
        bucket_names = []
        buckets = self._client.buckets_api().find_buckets().buckets
        for bucket in buckets:
            bucket_names.append(bucket.name)
        return bucket_names

    def addNewBucket(self, bucket_name):
        if bucket_name not in self.getBucketNames():
            retention_rules = BucketRetentionRules(type='expire',
                                                   every_seconds=0)
            self._client.buckets_api().create_bucket(\
                bucket_name=bucket_name,
                retention_rules=retention_rules, org=self._org)

    def readLastValues(self):
        """Queries InfluxDB for a last value of every existing key/subkey
        asyncronously, since thus the fastest response is obtained.
        For large DB this query can take minutes, therefore the last values
        are generally stored in a separate bucket. If the bucket with the latest
        values is empty for any reason this function shall be called.
        """

        def readKeys():
            msg = f'''import "influxdata/influxdb/schema"
                schema.measurements(bucket: "{self._bucket}",
                start: 2007-01-01T00:00:00Z, stop: now())'''
            tables = self._client.query_api().query(msg)
            keys = [record['_value'] for record in tables[0].records]
            return sorted(keys)

        def readSubkeys(client, key):
            msg = f'''import "influxdata/influxdb/schema"
                schema.measurementFieldKeys(bucket: "{self._bucket}",
                measurement: "{key}",
                start: 2007-01-01T00:00:00Z, stop: now())'''
            tables = client.query_api().query(msg)
            subkeys = [record['_value'] for table in tables for record in table]
            return sorted(subkeys)

        async def readSubkeysAsync(client, key):
            msg = f'''import "influxdata/influxdb/schema"
                schema.measurementFieldKeys(bucket: "{self._bucket}",
                measurement: "{key}",
                start: 2007-01-01T00:00:00Z, stop: now())'''
            tables = await client.query_api().query(msg)
            subkeys = [record['_value'] for table in tables for record in table]
            return sorted(subkeys)

        def readLastValue(client, key, subkey):
            result = []
            year = datetime.now().year
            while not result:
                if year < 2007:
                    break
                msg = f'''from(bucket:"{self._bucket}")
                    |> range(start: {year}-01-01T00:00:00Z, stop: now())
                    |> filter(fn:(r) => r._measurement == "{key}")
                    |> filter(fn:(r) => r._field == "{subkey}")
                    |> last(column: "_time")
                    |> drop(columns: ["_start", "_stop"])'''
                result = client.query_api().query(msg)
                year -= 1
            return result

        async def readLastValueAsync(client, key, subkey):
            result = []
            year = datetime.now().year
            while not result and year >= 2007:
                msg = f'''from(bucket:"{self._bucket}")
                    |> range(start: {year}-01-01T00:00:00Z, stop: now())
                    |> filter(fn:(r) => r._measurement == "{key}")
                    |> filter(fn:(r) => r._field == "{subkey}")
                    |> last(column: "_time")
                    |> drop(columns: ["_start", "_stop"])'''
                result = await client.query_api().query(msg)
                year -= 1
            return result

        def queryValues(client, keys):
            subkeys = [readSubkeys(client, key) for key in keys]
            keys = dict(zip(keys, subkeys))
            res = []
            for key, subkeys in keys.items():
                for subkey in subkeys:
                    res.append(readLastValue(client, key, subkey))
            return res

        async def queryValuesAsync(keys):
            async with InfluxDBClientAsync(url=self._url, token=self._token,
                                           org=self._org, timeout=300_000) as \
                    client:
                tasks = [readSubkeysAsync(client, key) for key in keys]
                keys = dict(zip(keys, await asyncio.gather(*tasks)))
                tasks = [readLastValueAsync(client, key, subkey)
                         for key, subkeys in keys.items() for subkey in subkeys]
                return await asyncio.gather(*tasks)

        keys = readKeys()
        result = asyncio.run(queryValuesAsync(keys)) \
                if hasattr(influxdb_client.client, 'influxdb_client_async') \
            else queryValues(self._client, keys)
        return result

    def init_query(self):
        """Returns last value for every key/subkey.
        Queries the DB for the latest values from a dedicated bucket. Compares
        number of entries, if they match queries the cache bucket for any newer
        values. If there is no match or there are no values, queries the cache
        bucket for the latest values.
        _start and _stop columns do not contain any valuable information, yet
        the influxdb-client module still parses them into datetime object.
        Dropping these columns saves 66% of computation time on the
        influxdb-client module side.
        Parsing of time codes from influxdb can be even faster if ciso8601
        module is installed.
        """

        self._update()
        result = []
        # query bucket with the latest values if exists and check if is complete
        last_ts, n_records = 0, 0
        if self._bucket_latest in self.getBucketNames():
            msg = f'''from(bucket:"{self._bucket_latest}")
                |> range(start: 2007-01-01T00:00:00Z, stop: now())
                |> drop(columns: ["_start", "_stop"])'''
            for table in self._client.query_api().query(msg):
                for record in table:
                    if record['_measurement'] == 'signing':
                        n_records = record['_value']
                        continue
                    last_ts = max(last_ts, record['_time'].timestamp())
                    result.append(record)
        if n_records != len(result):
            result = []

        # query the cache bucket for any newer values
        if last_ts and result:
            t1 = datetime.utcfromtimestamp(last_ts).strftime("%Y-%m-%dT%H:%M:%SZ")
            msg = f'''from(bucket:"{self._bucket}")
                |> range(start: {t1}, stop: now())
                |> last(column: "_time")
                |> drop(columns: ["_start", "_stop"])'''
            for table in self._client.query_api().query(msg):
                for record in table:
                    result.append(record)

        # query the cache bucket for the latest values
        if not result:
            for tables in self.readLastValues():
                for table in tables:
                    for record in table:
                        result.append(record)
        return result

    def queryLastValue(self, measurement, field, totime):
        self._update()
        t = datetime.utcfromtimestamp(totime).strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = f'''from(bucket:"{self._bucket}")
                |> range(start: 2007-01-01T00:00:00Z, stop: {t})
                |> filter(fn:(r) => r._measurement == "{measurement}")
                |> filter(fn:(r) => r._field == "{field}")
                |> last(column: "_time")
                |> drop(columns: ["_start", "_stop"])'''
        yield self._client.query_api().query_stream(msg)

    def queryHistory(self, measurement, field, fromtime, totime, interval):
        """Queries history from InfluxDB.
        """
        self._update()
        t1 = datetime.utcfromtimestamp(fromtime).strftime("%Y-%m-%dT%H:%M:%SZ")
        t2 = datetime.utcfromtimestamp(totime).strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = f'''from(bucket:"{self._bucket}")
                |> range(start: {t1}, stop: {t2})
                |> filter(fn:(r) => r._measurement == "{measurement}")
                |> filter(fn:(r) => r._field == "{field}")
                {f'|> aggregateWindow(every: {interval}s, fn: last, createEmpty: false)' if interval else ''}
                |> drop(columns: ["_start", "_stop"])'''
        yield self._client.query_api().query_stream(msg)

    def update(self, measurement, ts, field, value, expired):
        point = Point(measurement).time(ts).field(f'{field}', value)\
            .tag('expired', expired)
        value_float = self._convert_to_float(value)
        if value_float:
            point_float = Point(measurement).time(ts)\
                .field(f'{field}_float', value_float)\
                .tag('expired', expired)
        with self._update_lock:
            self._update_queue.append(point)
            if value_float:
                self._update_queue.append(point_float)
        if len(self._update_queue) > 100:
            self._update()

    def _update(self):
        with self._update_lock:
            self._write(self._bucket, self._update_queue)
            self._update_queue = []

    def writeLastValues(self, recent):
        bucket_id = \
            self._client.buckets_api().find_bucket_by_name(self._bucket_latest)
        if bucket_id:
            self._client.buckets_api().delete_bucket(bucket_id)

        points = []
        for measurement, (_, _, db) in recent.items():
            for field, entry in db.items():
                points.append(
                    Point(measurement)
                    .time(datetime.utcfromtimestamp(entry.time))
                    .field(field, entry.value)
                    .tag('expired', entry.expired)
                )
        if not self._bucket_latest in self.getBucketNames():
            self.addNewBucket(self._bucket_latest)
        self._write(self._bucket_latest, points)
        # signing
        self._write(self._bucket_latest, Point('signing')
                    .time(datetime.utcnow()).field('N_records', len(points)))


    def _write(self, bucket, points):
        self._write_api.write(bucket=bucket, record=points)

    def _convert_to_float(self, value):
        try:
            value = ast.literal_eval(value)
        except Exception:
            value = None
        if value:
            if type(value) in [list, tuple, set]:
                value = list(value)[0] if len(value) == 1 and \
                    type(list(value)[0]) not in [list, tuple, set, dict] \
                    else None
            if isinstance(value, int):
                value = float(value)
        return value if isinstance(value, float) else None


class InfluxDBCacheDatabase(CacheDatabase):
    """Cachedatabase descendant that stores values in InfluxDB.
    In InfluxDB 2.0 a database is called a bucket. Bucket name should be
    passed as a parameter. If a bucket with this name doesn't exist it will be
    created by the InfluxDB_client wrapper.
    This class also requires url of the database, access token and organization
    name, which are set up during installation and initialization of the
    InfluxDB.
    InfluxDB definitions are different to the ones used in NICOS. Nicos
    categories are stored as _measurements, nicos keys are organized in _fields.
    Values are stored as fields' _values. Expired mark is set up
    as _tag. It is better to keep expired as a tag, because then it is
    immideately available in every record obtained from queries. If expired is
    set up as field this field should be requested separately and this comes at
    higher computational cost.
    Values are stored as strings as they are in flatfile database for the sake
    of compatibility. If a value could be converted to float, then it will be
    stored as a float-copy to a special field: {field}_float. This field could
    be accessed through InfluxDB web interface or custom API queries.
    """

    parameters = {
        'url': Param(
            'URL of InfluxDB instance', type=str, mandatory=True
        ),
        'keystoretoken': Param(
            'Id used in the keystore for InfluxDB API token',
            type=str, default='influxdb', mandatory=True
        ),
        'org': Param(
            'Corresponding organization name created during initialization of '
            'InfluxDB instance', type=str, mandatory=True
        ),
        'bucket': Param(
            'Name of the bucket where data should be stored',
            type=str, default='nicos-cache', mandatory=False
        ),
        'bucket_latest': Param(
            'Name of the bucket where data should be stored',
            type=str, default='nicos-cache-latest-values', mandatory=False
        ),
    }

    def doInit(self, mode):
        self._recent = {}
        self._recent_lock = threading.Lock()
        CacheDatabase.doInit(self, mode)
        token = nicoskeystore.getCredential(self.keystoretoken)
        if not token:
            raise ConfigurationError('InfluxDB API token missing in keyring')
        self._client = InfluxDBWrapper(self.url, token, self.org, self.bucket,
                                       self.bucket_latest)
        self._time = datetime.now().timestamp()

    def initDatabase(self):
        records = self._client.init_query()
        for record in records:
            category = record['_measurement']
            subkey = record['_field']
            time = record['_time'].timestamp()
            with self._recent_lock:
                if category in self._recent:
                    _, lock, db = self._recent[category]
                    with lock:
                        db[subkey] = CacheEntry(time, None, record['_value'])
                        db[subkey].expired = record['expired'] == 'True'
                else:
                    db = {}
                    db[subkey] = CacheEntry(time, None, record['_value'])
                    db[subkey].expired = record['expired'] == 'True'
                    self._recent[category] = [None, threading.Lock(), db]

    def doShutdown(self):
        self._client.writeLastValues(self._recent)
        self._client.disconnect()

    def getEntry(self, dbkey):
        category, subkey = dbkey
        with self._recent_lock:
            if category not in self._recent:
                return None
            _, lock, db = self._recent[category]
        with lock:
            return db.get(subkey)

    def iterEntries(self):
        for cat, (_, lock, db) in list(self._recent.items()):
            with lock:
                for subkey, entry in db.items():
                    yield (cat, subkey), entry

    def updateEntries(self, categories, subkey, no_store, entry):
        if entry.time - self._time > 86400:
            self._client.writeLastValues(self._recent)
            self._time = entry.time

        real_update = True
        for cat in categories:
            with self._recent_lock:
                if cat not in self._recent:
                    self._recent[cat] = [None, threading.Lock(), {}]
                _, lock, db = self._recent[cat]
            update = True
            with lock:
                if subkey in db:
                    curentry = db[subkey]
                    if curentry.value == entry.value and not curentry.expired:
                        curentry.time = entry.time
                        curentry.ttl = entry.ttl
                        update = real_update = False
                    elif entry.value is None and curentry.expired:
                        update = real_update = False
                if update:
                    db[subkey] = entry
                    if not no_store:
                        time = datetime.utcfromtimestamp(entry.time)
                        self._client.update(cat, time, subkey, entry.value,
                                            entry.expired)
        return real_update

    def queryHistory(self, dbkey, fromtime, totime, interval):
        empty = True
        category, subkey = dbkey
        for records in self._client.queryHistory(category, subkey, fromtime,
                                                 totime, interval):
            for record in records:
                empty = False
                time = record['_time'].timestamp()
                entry = CacheEntry(time, None, record['_value'])
                entry.expired = record['expired'] == 'True'
                yield entry
        if empty:
            for records in self._client.queryLastValue(category, subkey, fromtime):
                for record in records:
                    time = record['_time'].timestamp()
                    entry = CacheEntry(time, None, record['_value'])
                    entry.expired = record['expired'] == 'True'
                    yield entry
