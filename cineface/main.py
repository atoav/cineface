#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import time
import importlib_metadata

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_message_builder
from pythonosc import udp_client
from gpiozero import Button

from cineface.config import Config, init_config
from cineface.helpers import fit, clamp, lerp
from cineface.totalmix import Output, Outputs
from cineface.display import VolumeDisplay, LevelDisplay


VERSION = importlib_metadata.metadata(__package__)["Version"]
APPLICATION_NAME = importlib_metadata.metadata(__package__)["Name"]
LICENSE = importlib_metadata.metadata(__package__)["License"]
AUTHOR = importlib_metadata.metadata(__package__)["Author"]



# Load configuration
config = init_config()

# Create Outputs Collection
outputs = Outputs().from_config(config)

# Create Displays
volume_display = VolumeDisplay().from_config(config)
level_display  = LevelDisplay().from_config(config)
print("============== Setup done ===============\n")






def update_outputs(addr, value):
    """
    Read values received from totalmix and set the value of state to it.
    Called via Dispatcher Callback. Everything that should react to messages
    sent to this script via OSC should go here
    """
    global outputs
    global volume_display

    for output in outputs:
        if output.is_valid_address(addr):
            output.update(addr, value)
            # print(output.as_table())


async def loop():
    """
    Asynchronous Loop reads buttons, faders etc and send messages to totalmix
    """
    global outputs
    global volume_display
    global level_display
    frames = 0

    while True:
        # Update & Draw the levels display (if it is activated in the config)
        volume_display.update(outputs.volume_db, outputs.has_uniform_volume)
        volume_display.draw()

        # Draw the levels display (if it is activated in the config)
        level_display.draw(outputs)

        frames += 1
        await asyncio.sleep(0.01)


async def init_main():
    """
    Asynchronous main, to be called from main()
    """
    global config
    global outputs

    print("Setting up dispatcher")
    dispatcher = Dispatcher()
    dispatcher.map("/*", update_outputs)

    print("Starting Client for {}:{}".format(config["Client"]["ip"], config["Client"]["port"]))
    client = udp_client.SimpleUDPClient(config["Client"]["ip"], config["Client"]["port"])
    client.send_message("/setBankStart", 1.0)
    client.send_message("/1/busOutput", 1.0)
    outputs.register_client(client)

    print("Starting Server at {}:{}".format(config["Server"]["ip"], config["Server"]["port"]))
    server = AsyncIOOSCUDPServer((config["Server"]["ip"], config["Server"]["port"]), dispatcher, asyncio.get_event_loop())
    
    # Create datagram endpoint and start serving
    transport, protocol = await server.create_serve_endpoint()

    print("Listening...")
    await loop()

    transport.close()


def main():
    """
    Entry point, run this to run the programme
    """
    
    asyncio.run(init_main())


if __name__ == "__main__":
    main()