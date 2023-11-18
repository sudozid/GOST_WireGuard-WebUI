# GOST_WireGuard-WebUI
 A flask program to have traffic from SOCKS/HTTP Proxies using GOST to be forwarded to WireGuard Interfaces.

# What it does

1. You can add WireGuard configs from VPN Providers (Mullvad, AirVPN etc).
2. You can make GOST commands to have SOCKS/HTTP proxies forward the traffic to previously setup WireGuard interface.

The code is dogshit I know, I'm not a regular coder and made most of it with the help of ChatGPT. If you feel like this is something useful for you, you can fork or idk start from scratch. 

- 'Save Active Interfaces' will save all the WireGuard interfaces which are up to a text file called 'active_interfaces.txt'. This will be auto-started next time the container starts, see entrypoint.sh for more details.
- 'Save Command' in GOST section will save the GOST command generated from the parameters specified by the user to a txt file which will be auto-started, again, see entrypoint.sh for more details.

Are there better ways to do this? Probably, but for me it was about getting it up as fast as possible since I do not wish to spend more than three days on this project.

![alt text](https://github.com/sudozid/GOST_WireGuard-WebUI/blob/main/ss1.png)

![alt text](https://github.com/sudozid/GOST_WireGuard-WebUI/blob/main/ss2.png)


You can run it with 

`python3 api.py` 

Docker command (not secure, run only on a private network!). You can also remove --net=host, have it run in a bridge network and have the webui be reverse proxied with basic auth using NGINX. I was just testing.

`
docker run -d  --name testing   -v "$(pwd)/parameters.csv:/usr/src/app/parameters.csv"   -v "$(pwd)/active_interfaces.txt:/usr/src/app/active_interfaces.txt"   -v "$(pwd)/gost_command.txt:/usr/src/app/gost_command.txt"   -v "$(pwd)/wg_configs:/etc/wireguard"  --privileged -p 54324:8000 -p 4201:4201  --net=host gost_wg_webui
`
