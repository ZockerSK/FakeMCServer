# FakeMCServer

This program creates a simple Minecraft protocol wrapper, which imitates a full Minecraft server. This can be used to respond to pings with some information provided without the need to start a (Java) server.

![Overview](https://raw.githubusercontent.com/ZockerSK/FakeMCServerImages/main/overview.png)

You can start this program by using
```
$ python3 main.py
```

Example configuration:
```json
{
    "ip": "0.0.0.0",
    "kick_message": [
        "§bSorry",
        "",
        "§aThis server is offline!"
    ],
    "motd": {
        "1": "§4Maintenance!",
        "2": "§aCheck example.com for more information!"
    },
    "port": 25565,
    "protocol": 2,
    "samples": [
        "§bexample.com",
        "",
        "§4Maintenance"
    ],
    "server_icon": "server_icon.png",
    "show_hostname_if_available": true,
    "show_ip_if_hostname_available": true,
    "version_text": "§4Maintenance",
    "player_max": 0,
    "player_online": 0
}
```
Please note, that the `server_icon` **must** be 64x64 and a png file.

In this configuration you can use typical Minecraft message formatting tags.

`show_..._if_available` enables/disables the resolution of the hostname of the ip/that the IP will be displayed, if the hostname is available

`protocol` is the server's game version ID (see [wiki.vg](https://wiki.vg/Protocol_version_numbers) for more details)

`samples` specifies the player displayed when hovering over the player count/version information.

![Samples](https://raw.githubusercontent.com/ZockerSK/FakeMCServerImages/main/samples.png)

## Contribution
If you find some issues or encounter problems, feel free to write an issue providing your problem and some information regarding your setup (like Minecraft version, python version, ...).
