InfluxDB2 installation and setup
--------------------------------

In order to install InfluxDB instance, best to follow official
`guide <https://docs.influxdata.com/influxdb/v2.0/install/>`_.

Initial setup can be implemented through InfluxDB2 web interface or via CLI.
One needs to specify organization name, initial bucket, username and password::

   influx setup -o mlz -b nicos-cache -u nicos -p password -f

The API token should be generated at the previous step. If not please check
the official documentation for the version of InfluxDB which is running.
Generated token can be accessed via both web interface and command::

   influx config ls --json

The token should be stored in nicos keystore as a new field "influxdb"::

   bin/nicos-keystore add influxdb --storagepw nicos --password [token]

Start InfluxDB2 service with telemetry disabled::

   influxd --reporting-disabled

