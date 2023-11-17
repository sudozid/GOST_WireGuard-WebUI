# GOST_WireGuard-WebUI
 A flask program to have traffic from SOCKS/HTTP Proxies using GOST to be forwarded to WireGuard Interfaces.

# What it does

1. You can add WireGuard configs from VPN Providers (Mullvad, AirVPN etc).
2. You can make GOST commands to have SOCKS/HTTP proxies forward the traffic to previously setup WireGuard interface.

The code is dogshit I know, I'm not a regular coder and made most of it with the help of ChatGPT. If you feel like this is something useful for you, you can fork or idk start from scratch.

You can run it with 

`python3 api.py` 

Docker command (not secure, run only on a private network!)

`
docker run -d  --name testing   -v "$(pwd)/parameters.csv:/usr/src/app/parameters.csv"   -v "$(pwd)/active_interfaces.txt:/usr/src/app/active_interfaces.txt"   -v "$(pwd)/gost_command.txt:/usr/src/app/gost_command.txt"   -v "$(pwd)/wg_configs:/etc/wireguard"  --privileged -p 54324:8000 -p 4201:4201  --net=host gost_wg_webui
`
