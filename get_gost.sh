#!/bin/bash

# Define the GitHub API URL
API_URL="https://api.github.com/repos/go-gost/gost/releases"

# Get the latest release JSON
latest_release=$(curl -s "$API_URL" | jq -r '.[0]')

# Extract the binary URL and tag name
binary_url=$(echo "$latest_release" | jq -r '.assets[] | select(.name | endswith("linux_amd64v3.tar.gz")) | .browser_download_url')
tag_name=$(echo "$latest_release" | jq -r '.tag_name')

# Create a temporary directory to work in
tmp_dir=$(mktemp -d)

# Download and extract the binary
cd "$tmp_dir" || exit
curl -L -o "$tag_name.tar.gz" "$binary_url"
tar -xzvf "$tag_name.tar.gz"

# Copy the 'gost' binary to the desired location (e.g., /usr/local/bin/)
cp "$tmp_dir/gost" /bin
