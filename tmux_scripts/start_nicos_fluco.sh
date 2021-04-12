#!/bin/sh
session="nicos"

tmux start-server
tmux new-session -d -s $session

tmux new-window -t $session:1 -n cache
tmux send-keys "source venv/bin/activate" C-m
tmux send-keys "bin/nicos-cache" C-m

tmux new-window -t $session:2 -n poller
tmux send-keys "source venv/bin/activate" C-m
tmux send-keys "bin/nicos-poller" C-m

tmux new-window -t $session:3 -n daemon
tmux send-keys "source venv/bin/activate" C-m
tmux send-keys "bin/nicos-daemon" C-m
