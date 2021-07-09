How To Use the iPython NICOS Interface
=========================================

After starting ipython, load the extension:

    %load_ext nicos.clients.ipython.nicos

You may also put this code into ~/.ipython/profile_default_startup/01-nicos.ipy

| import os
| nicosdir=os.getenv(NICOSROOT)
| olddir = os.getcwd()
| os.chdir(nicosdir)
| %load_ext nicos.clients.ipython.nicos
| os.chdir(olddir)

in order to load the ipython nicos client automatically at ipython startup. Change nicosdir to
match your installation of NICOS. Or set the environment variable NICOSROOT.
Note that the .ipy extension is REQUIRED for this to work.

Connect to a NICOS server with:

    %nicos /connect <host> <port> <user> <password>

Then issue NICOS commands with:

    %nicos <command>

You will get all the output from the command. This will also run commands when
the underlying NICOS is running another script. Reading commands will work, other
commands will yield an error.

Get device values from nicos with:

    var = %nicos /val <device>

Get device parameters from NICOS with:

    var = %nicos /val <device.param>

Test the status of NICOS

    %nicos /status

Get access to live data with:

    var = %nicos /val <detname>_live

List available live data entries with:

    %nicos /live

Read scan data with:

    x, y, n = %nicos /val scandata

x the contains the x axis data, y the counts and n the names of the variables used for each.

detname must be the name of the detector issuing the live data. The returned var
is a list of arrays.

Disconnect from NICOS with

   %nicos /quit

