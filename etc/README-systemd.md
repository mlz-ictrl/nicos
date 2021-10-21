Enable NICOS start/stop via systemd
===================================

This document describe the steps needed to use the systemd to start/stop NICOS
services from checkout.  This readme does not apply to properly packaged
versions.

1. First ensure that the needed systemd directories exist:

   mkdir -p /lib/systemd/scripts/
   mkdir -p /lib/systemd/system/

2. Create some symlink from the current NICOSROOT dir into the systemd structure:

   ln -sf $(NICOSROOT)/etc/nicos-late-generator /lib/systemd/scripts/
   ln -sf $(NICOSROOT)/etc/nicos-late-generator.service /lib/systemd/system/
   ln -sf $(NICOSROOT)/etc/nicos.target /lib/systemd/system/

3. Create the NICOS services units, the needed services are defined in the
   $(NICOSROOT)/nicos.conf 'services' entry:

   systemctl enable --now nicos-late-generator

4. Enable the nicos services:

   systemctl enable nicos.target
