# SINQ NICOS Scripts

At SINQ we have NICOS installed under a special nicos account. This is where all
the git stuff is happening. NICOS is run in a virtual environment. This
directory contains some  scripts which basically activate the correct
virtualenv and then do the NICOS things. As of 04/2019, this is actually
working. Available scripts:

- **nicosctl** For starting and stopping NICOS. Basically a wrapper arouent
  etc/nicos-system.
- **local/nicos-gui, local-nicos-cli**, scripts for starting NICOS clients
  locally
- **nicos-gui, nicos-cli**, we have a central NICOS installation for the user
  interface somehwere on AFS. These two script activate the suitable environment
  and start the client software.
- **tmuxnicos** runs NICOS with a virtual environment in detacched terminals under
  tmux. This is the version used for development
- **tmuxnicos-inst** is the same as tmuxnicos but for running this on an
  instrument
- **nicos-env** A script to start a NICOS daemon within a virtual environment
- **nicos-env-dev** same as above but configured for the development
  environment


