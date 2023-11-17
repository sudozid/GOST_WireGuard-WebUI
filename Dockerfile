# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install WireGuard tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends procps iproute2 wireguard-tools curl jq bash screen && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Copy entrypoint script into the container
COPY entrypoint.sh /usr/src/app/entrypoint.sh

# Make entrypoint.sh executable
RUN chmod +x /usr/src/app/entrypoint.sh

RUN chmod +x get_gost.sh
RUN /bin/bash get_gost.sh

# Use entrypoint.sh as the entry point for the container
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
