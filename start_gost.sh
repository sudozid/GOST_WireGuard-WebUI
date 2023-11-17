#!/bin/bash

# Define the command to start gost
gost_command=$(cat gost_command.txt)

# Start the gost command in a screen session
screen -dmS gost_autostart bash -c "$gost_command"

# Print a message indicating that gost has been started
echo "gost_autostart screen session has been started with the following command:"
echo "$gost_command"
