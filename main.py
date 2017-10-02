#!/usr/bin/env python3

import base64
import json
import os.path

from socket_server import SocketServer

server = None


def main():
    if os.path.exists("config.json"):
        with open("config.json", 'r') as file:
            configuration = json.load(file)

        ip = configuration["ip"]
        port = configuration["port"]
        motd = configuration["motd"]["1"] + "\n" + configuration["motd"]["2"]
        version_text = configuration["version_text"]
        kick_message = ""
        samples = configuration["samples"]
        server_icon = None

        for message in configuration["kick_message"]:
            kick_message += message + "\n"
        kick_message = kick_message[:-2]

        if not os.path.exists(configuration["server_icon"]):
            print("Server icon doesn't exists - submitting none...")
        else:
            with open(configuration["server_icon"], 'rb') as image:
                server_icon = "data:image/png;base64," + base64.b64encode(image.read()).decode()
        try:
            global server
            server = SocketServer(ip, port, motd, version_text, kick_message, samples, server_icon)
            server.start()
        except KeyboardInterrupt:
            server.close()
            exit(1)
        except Exception as e:
            print(e)
    else:
        configuration = {}
        configuration["ip"] = "0.0.0.0"
        configuration["port"] = 25565
        configuration["motd"] = {}
        configuration["motd"]["1"] = "§4Maintenance!"
        configuration["motd"]["2"] = "§aCheck example.com for more information!"
        configuration["version_text"] = "§4Maintenance"
        configuration["kick_message"] = ["§bSorry", "", "§aThis server is offline!"]
        configuration["server_icon"] = "server_icon.png"
        configuration["samples"] = ["§bexample.com", "", "§4Maintenance"]

        with open("config.json", 'w') as file:
            json.dump(configuration, file, sort_keys=True, indent=4, ensure_ascii=False)

        print("[!] A new configuration was created!")
        print("Please check the settings in the config.json!")
        exit(1)


if __name__ == '__main__':
    main()
