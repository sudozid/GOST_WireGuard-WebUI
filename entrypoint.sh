#!/bin/sh

# Exit on any error
set -e

# Print a message indicating that Gunicorn has been started in a screen session
echo "Gunicorn has been started in a screen session named 'gunicorn_autostart'."

# Your other script contents follow...
gost_command=$(cat gost_command.txt)

# Start the gost command in a screen session
screen -dmS gost_autostart bash -c "$gost_command"

# Print a message indicating that gost has been started
echo "gost_autostart screen session has been started with the following command:"
echo "$gost_command"

# Check if the active_interfaces.txt file exists
active_interfaces_file="active_interfaces.txt"
if [ ! -e "$active_interfaces_file" ]; then
    echo "Error: active_interfaces.txt not found."
    exit 1
fi

# Read the file line by line and run "wg-quick up" for each interface
while IFS= read -r interface_name; do
    if [ -n "$interface_name" ]; then
        echo "Bringing up WireGuard interface: $interface_name"
        wg-quick up "$interface_name"
        if [ $? -eq 0 ]; then
            echo "Successfully brought up $interface_name."
        else
            echo "Failed to bring up $interface_name."
        fi
    fi
done < "$active_interfaces_file"

gunicorn --workers=3 --bind=0.0.0.0:8000 'api:app'
