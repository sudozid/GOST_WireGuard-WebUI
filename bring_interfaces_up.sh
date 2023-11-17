#!/bin/bash

# Define the path to the active_interfaces.txt file
active_interfaces_file="active_interfaces.txt"

# Check if the file exists
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
