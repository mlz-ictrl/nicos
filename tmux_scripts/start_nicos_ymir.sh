#!/bin/sh
session="nicos"

tmux start-server
tmux new-session -d -s $session

tmux new-window -t $session:1 -n cache
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-cache" C-m

tmux new-window -t $session:2 -n poller
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-poller" C-m

tmux new-window -t $session:3 -n daemon
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-daemon" C-m

tmux new-window -t $session:4 -n forwarder
tmux send-keys "export EPICS_CA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_CA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "export EPICS_PVA_AUTO_ADDR_LIST=NO" C-m
tmux send-keys "export EPICS_PVA_ADDR_LIST='172.30.238.79'" C-m
tmux send-keys "bin/nicos-forwarder -b 172.30.242.20:9092 -t ymir_nicos_devices" C-m
