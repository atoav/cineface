#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import toml
from typing import NewType, Optional, Tuple, Iterable, List
from collections.abc import MutableMapping
import os, sys
import importlib_metadata

import appdirs

VERSION = importlib_metadata.metadata(__package__)["Version"]
APPLICATION_NAME = importlib_metadata.metadata(__package__)["Name"]
LICENSE = importlib_metadata.metadata(__package__)["License"]
AUTHOR = importlib_metadata.metadata(__package__)["Author"]


EXAMPLE_CONFIG = """# ======= CINEFACE CONFIGURATION FILE =======
# Cineface talks to RME Totalmix via OSC and controls it's outputs

[Client]
# Address for the UDP Client
ip = "192.168.178.81"
port = 7001

[Server]
# Address/Port for the OSC Server
ip = "0.0.0.0"
port = 9001

# You can add more outputs or leave some out if you like by 
# adding/removing [[Output]] blocks

[[Output]]
name = "headphones"
address = "/1/volume5"
stereo = true
gpio_button = 25
gpio_led = 24

[[Output]]
name = "speakers"
address = "/1/volume1"
stereo = true
gpio_button = 10
gpio_led = 9

[[Output]]
name = "center"
address = "/1/volume2"
stereo = false
gpio_button = 14
gpio_led = 15

[[Output]]
name = "lfe"
address = "/1/volume3"
stereo = false
gpio_button = 18
gpio_led = 17

[[Output]]
name = "rear"
address = "/1/volume4"
stereo = true
gpio_button = 23
gpio_led = 22

"""





class Config(MutableMapping):
    """
    A dictionary that applies an arbitrary key-altering
    function before accessing the keys
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def from_disk(self, path: str) -> 'Config':
        """
        Read config from a given path.
        """
        with open(path, encoding='utf-8') as c:
            try:
                config = toml.loads(c.read())
            except toml.TomlDecodeError as e:
                print("Error: There was a syntax error in the configuration file at \"{}\":".format(path), file=sys.stderr)
                print(e, file=sys.stderr)
                print()
                print("Hint: fix the Syntax Errors or delete/rename the file to generate a new default config")
                exit(1)
            self.store = config

        print("Read config from {}".format(path))
        return self

    def is_good(self) -> bool:
        """
        Check the Configuration for missing fields
        """
        example_config = toml.loads(EXAMPLE_CONFIG)
        ok = True
        for s in example_config.keys():
            if not s in self.keys():
                print("Error: Your configuration misses the section: [{}]".format(s), file=sys.stderr)
                ok = False
            else:
                if type(example_config[s]) == dict:
                    for v in example_config[s].keys():
                        if not v in self[s].keys():
                            print("Error: Your configuration misses the field \"{}\" in the section: [{}]".format(v, s), file=sys.stderr)
                            ok = False
                elif type(example_config[s]) == list:
                    for listelement in example_config[s]:
                        for v in listelement.keys():
                            if not v in self[s][0].keys():
                                print("Error: Your configuration misses the field \"{}\" in the section: [{}]".format(v, s), file=sys.stderr)
                                ok = False

        if not ok:
            print("Hint: You can delete your configuration and cineface will write a new default one")

        return ok



def init_config() -> Optional[Config]:
    """
    Read the config from the user config path. 
    If there is no config yet, propose the generation of a new one
    """

    # Get OS dependend properties file
    user_config_path = get_user_config_path()

    # Check if we are on the server and try to read that properties file first
    if os.path.isfile(user_config_path):
        config = Config().from_disk(user_config_path)
        if config.is_good():
            return config
        else:
            exit()
    else:
        new_config(user_config_path)


def new_config(user_config_path: str, skip_prompt: bool=True):
    """
    Warn users that there was no config file found, and then ask them if they want to create one.
    The skip_prompt flag can be used to invoke this without asking or printing (e.g.
    if asking and printing should be done elsewhere)
    """
    # Create all directories in the path to the config, if they don't exist yet
    try:
        os.makedirs(user_config_path.rstrip("{}.toml".format(APPLICATION_NAME)))
    except FileExistsError:
        pass

    # Write default config
    with open(user_config_path, "w") as f:
        for line in EXAMPLE_CONFIG.splitlines():
            f.write("{}\n".format(line))

    # Open with standard editor
    if os.name == 'nt':
        os.system("notepad.exe {}".format(user_config_path))
    else:
        os.system("$EDITOR {}".format(user_config_path))

    exit()


def get_user_config_path() -> str:
    """
    Return the user config path
    """
    user_config_path = appdirs.user_config_dir(APPLICATION_NAME)
    user_config_path = "{}.toml".format(user_config_path)
    return user_config_path
