#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image


class VolumeDisplay():

    def __init__(self):
        self.serial = None
        self.device = None
        self.font   = None
        self.value  = None

    def from_config(self, config) -> 'VolumeDisplay':
        # Temporary Variables
        address = config["VolumeDisplay"]["i2c_address"]
        port = config["VolumeDisplay"]["i2c_port"]
        font = config["VolumeDisplay"]["font"]
        size = config["VolumeDisplay"]["size"]

        # Set the initial values
        self.serial = i2c(port=port, address=address)
        self.device = sh1106(self.serial)
        self.font = ImageFont.truetype(font, size)

        return self

    @property
    def text(self):
        if self.value is None:
            return "n.a."
        if self.value == 0.0:
            return " 0.0"
        elif self.value <= -65.0:
            return "-∞"
        elif self.value > 0.0:
            return "+{:.1f}".format(self.value)
        elif self.value < 0.0:
            return "{:.1f}".format(self.value)

    def draw(self):
        with canvas(self.device) as draw:
            # draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((0, 5), self.text, font=self.font, fill="white")

    def update(self, value):
        self.value = float(value)