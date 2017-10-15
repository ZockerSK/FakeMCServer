#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import base64
import json
import os.path

from socket_server import SocketServer

server = None


def main():
    logger = logging.getLogger("FakeMCServer")
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler("logs/access.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    if os.path.exists("config.json"):
        logger.info("Loading configuration...")
        with open("config.json", 'r') as file:
            configuration = json.load(file)

        ip = configuration["ip"]
        port = configuration["port"]
        motd = configuration["motd"]["1"] + "\n" + configuration["motd"]["2"]
        version_text = configuration["version_text"]
        kick_message = ""
        samples = configuration["samples"]
        show_ip = configuration["show_ip_if_hostname_available"]

        if show_ip is None:
            configuration["show_ip_if_hostname_available"] = True
            show_ip = True
            with open("config.json", 'w') as file:
                json.dump(configuration, file, sort_keys=True, indent=4, ensure_ascii=False)

        server_icon = None

        for message in configuration["kick_message"]:
            kick_message += message + "\n"

        if not os.path.exists(configuration["server_icon"]):
            logger.warning("Server icon doesn't exists - submitting none...")
        else:
            with open(configuration["server_icon"], 'rb') as image:
                server_icon = "data:image/png;base64," + base64.b64encode(image.read()).decode()
        try:
            global server
            logger.info("Setting up server...")
            server = SocketServer(ip, port, motd, version_text, kick_message, samples, server_icon, logger, show_ip)
            server.start()
        except KeyboardInterrupt:
            logger.info("Shutting down server...")
            server.close()
            logger.info("Done. Thanks for using FakeMCServer!")
            exit(0)
        except Exception as e:
            logger.exception(e)
    else:
        logger.warning("No configuration file found. Creating config.json...")
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
        configuration["show_ip_if_hostname_available"] = True

        with open("config.json", 'w') as file:
            json.dump(configuration, file, sort_keys=True, indent=4, ensure_ascii=False)
        logger.info("Please adjust the settings in the config.json!")
        exit(1)


if __name__ == '__main__':
    main()
