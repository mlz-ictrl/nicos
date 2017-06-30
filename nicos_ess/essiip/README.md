# Instructions for pvaccess test

There is an example setup based on a Lewis simulation that
exposes a device via ChannelAccess. For Lewis to work,
an EPICS base installation is required, because it uses
pcaspy.

Running the simulation:

    $ git clone https://github.com/MichaelWedel/lewis-epics-examples.git
    $ cd lewis-epics-examples
    $ pip install -r requirements.txt
    $ lewis -a . -k devices -p "epics: {prefix: 'Motor1:'}" epics_motor

To verify that the PVs can be accessed use a different terminal:

    $ caget Motor1:Pos
    0.0

Now this device is accessible in NICOS:

    $ cd $NICOS_CORE_DIRECTORY
    $ INSTRUMENT=essiip ./bin/nicos-demo -MEW

Load the `lewis_motor`-setup. If the EPICS environment
is setup correctly and `pvaPy` is available (as `pvaccess.so`), that should work.
