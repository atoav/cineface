#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image


def center_text(img, font, text, color=(255, 255, 255)):
    draw = ImageDraw.Draw(img)
    text_width, text_height = draw.textsize(text, font)
    position = ((strip_width-text_width)/2,(strip_height-text_height)/2)
    draw.text(position, text, color, font=font)
    return img


class VolumeDisplay():
    """
    A SH1106 OLED Display that will display the current dialed in volume in dB
    the value will be updated and drawn in the main loop and is derived from the
    Outputs class found in totalmix.py

    If the volumes of all unmuted channels that aren't named headphones doesn't line
    up (so e.g. if the Center channel is accidentally dimmed by -3 dB) a white square
    is displayed in the top left corner.

    If the VolumeDisplay is set to inactive in the config, it is not loaded at all
    and does nothing (otherwise there will be an error if no display is connected)
    """

    def __init__(self):
        self.active = False
        self.serial = None
        self.device = None
        self.font   = None
        self.value  = None
        self.has_uniform_volume = True

    def from_config(self, config) -> 'VolumeDisplay':
        # Temporary Variables
        active  = config["VolumeDisplay"]["active"]
        address = config["VolumeDisplay"]["i2c_address"]
        port    = config["VolumeDisplay"]["i2c_port"]
        font    = config["VolumeDisplay"]["font"]
        size    = config["VolumeDisplay"]["size"]

        # Set the initial values
        self.active = active
        if self.active:
            self.serial = i2c(port=port, address=address)
            self.device = sh1106(self.serial)
            self.font = ImageFont.truetype(font, size)

            print("Setting up LevelDisplay at i2c address {}".format(address))

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
        if self.active:
            with canvas(self.device) as draw:
                # draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text((0, 5), self.text, font=self.font, fill="white")

                # If not all channels have uniform volume, draw a white square as warning
                if not self.has_uniform_volume:
                    draw.rectangle([(0, 0), (10, 10)], outline="white", fill="white")

    def update(self, value, has_uniform_volume=True):
        if self.active:
            self.value = float(value)
            self.has_uniform_volume = has_uniform_volume




class LevelDisplay():
    """
    A SH1106 OLED Display that will display the current dialed in volume in dB
    the value will be updated and drawn in the main loop and is derived from the
    Outputs class found in totalmix.py

    If the volumes of all unmuted channels that aren't named headphones doesn't line
    up (so e.g. if the Center channel is accidentally dimmed by -3 dB) a white square
    is displayed in the top left corner.

    If the LevelDisplay is set to inactive in the config, it is not loaded at all
    and does nothing (otherwise there will be an error if no display is connected)
    """

    def __init__(self):
        self.active = False
        self.serial = None
        self.device = None
        self.font   = None
        self.min_height = 2
        self.slotwidth = 128//9
        self.margin_bottom = 10
        self.margin_top = 0
        self.h = 64
        self.w = 128
        self.b = self.h - self.margin_bottom
        self.barheight = self.h - self.margin_bottom - self.margin_top
        self.barwidth  = 8
        self.gutter = (self.slotwidth-self.barwidth)/2

    def from_config(self, config) -> 'LevelDisplay':
        # Temporary Variables
        active  = config["LevelDisplay"]["active"]
        address = config["LevelDisplay"]["i2c_address"]
        port    = config["LevelDisplay"]["i2c_port"]
        left    = config["LevelDisplay"]["left"]
        right   = config["LevelDisplay"]["right"]

        # Set the initial values
        self.active = active
        if self.active:
            self.serial = i2c(port=port, address=address)
            self.device = sh1106(self.serial)
            self.font = ImageFont.truetype("fonts/Inter-Medium.ttf", 10)
            self.left = left
            self.right = right

            print("Setting up LevelDisplay at i2c address {}".format(address))

        return self


    def draw(self, outputs):

        # if inactive just return
        if not self.active:
            return

        # Draw on canvas
        with canvas(self.device) as draw:
            n = 0
            # Draw the left aligned outputs first
            for output in [o for o in outputs if o.name is not None and o.name in self.left]:
                # If the outputs aren't ready yet just skip drawing them
                if output.stereo and (output.levels["L"] is None or output.levels["R"] is None or output.mute is None):
                    continue

                # Do the same for mono outputs
                if not output.stereo and (output.levels is None or output.mute is None):
                    continue

                # Draw level meter bars
                if output.stereo:
                    # Stereo channels take up two slots
                    draw.rectangle([(n*self.slotwidth, self.b+output.levels["L"]*-50), (n*self.slotwidth+self.barwidth, self.b)], outline="white", fill="white")
                    n += 1
                    draw.rectangle([(n*self.slotwidth, self.b+output.levels["R"]*-50), (n*self.slotwidth+self.barwidth, self.b)], outline="white", fill="white")
                    n += 1
                else:
                    # Mono channels take up one slot
                    draw.rectangle([(n*self.slotwidth, self.b+output.levels*-50), (n*self.slotwidth+self.barwidth, self.b)], outline="white", fill="white")
                    n += 1

                # Draw Channel Names and Mute icons
                if output.mute and not output.stereo:
                    # Draw Mute Icon if channel muted
                    x = n-1
                    draw.rectangle([(x*self.slotwidth, self.b+2), (x*self.slotwidth+self.barwidth, self.h)], outline="white", fill="white")
                    draw.text((x*self.slotwidth, self.b), "M", font=self.font, fill="black")
                elif output.mute and output.stereo:
                    # Draw Mute Icon if channel muted
                    x = n-2
                    draw.rectangle([(x*self.slotwidth, self.b+2), (x*self.slotwidth+self.slotwidth+self.barwidth, self.h)], outline="white", fill="white")
                    draw.text((x*self.slotwidth+(self.slotwidth//2), self.b), "M", font=self.font, fill="black")
                elif output.stereo:
                    # Display short output name if not muted
                    x = n-2
                    text = output.short
                    w, h = draw.textsize(text, self.font)
                    center = (x*self.slotwidth+self.slotwidth-self.gutter/2, self.b)
                    coords = (center[0]-w/2, self.b)
                    draw.text(coords, text, font=self.font, fill="white")
                elif not output.stereo:
                    # Display short output name if not muted
                    x = n-1
                    text = output.short
                    w, h = draw.textsize(text, self.font)
                    center = (x*self.slotwidth+self.barwidth/2, self.b)
                    coords = (center[0]-w/2, self.b)
                    draw.text(coords, text, font=self.font, fill="white")

            # Draw right aligned outputs here (see config)
            n = 0
            for output in [o for o in outputs if o.name is not None and o.name in self.right]:
                # If the outputs aren't ready yet just skip drawing them
                if output.stereo and (output.levels["L"] is None or output.levels["R"] is None or output.mute is None):
                    continue

                # Do the same for mono outputs
                if not output.stereo and (output.levels is None or output.mute is None):
                    continue
                # Draw level meter bars
                if output.stereo:
                    draw.rectangle([(self.w-(n*self.slotwidth), self.b+output.levels["R"]*-50), (self.w-(n*self.slotwidth+self.barwidth), self.b)], outline="white", fill="white")
                    n += 1
                    draw.rectangle([(self.w-(n*self.slotwidth), self.b+output.levels["L"]*-50), (self.w-(n*self.slotwidth+self.barwidth), self.b)], outline="white", fill="white")
                    n += 1
                else:
                    draw.rectangle([(self.w-(n*self.slotwidth), self.b+output.levels*-50), (self.w-(n*self.slotwidth+self.barwidth), self.b)], outline="white", fill="white")
                    n += 1

                # Draw Channel Names and Mute icons
                if output.mute is not None:
                    if output.mute and not output.stereo:
                        # Display "M" Mute label if muted
                        x = n-1
                        draw.rectangle([(self.w-(x*self.slotwidth), self.b+2), (self.w-(x*self.slotwidth+self.barwidth), self.h)], outline="white", fill="white")
                        draw.text((self.w-(x*self.slotwidth), self.b), "M", font=self.font, fill="black")
                    elif output.mute and output.stereo:
                        # Display "M" Mute label if muted
                        x = n-2
                        draw.rectangle([(self.w-(x*self.slotwidth), self.b+2), (self.w-(x*self.slotwidth+self.slotwidth+self.barwidth), self.h)], outline="white", fill="white")
                        draw.text((self.w-(x*self.slotwidth+self.slotwidth+1), self.b), "M", font=self.font, fill="black")
                    elif output.stereo:
                        # Display short output name if not muted
                        x = n-2
                        text = output.short
                        w, h = draw.textsize(text, self.font)
                        center = (self.w-self.slotwidth+self.gutter, self.b)
                        coords = (center[0]-w/2, self.b)
                        draw.text(coords, text, font=self.font, fill="white")
                    elif not output.stereo:
                        # Display short output name if not muted
                        x = n-1
                        text = output.short
                        w, h = draw.textsize(text, self.font)
                        center = (self.w-self.slotwidth, self.b)
                        coords = (center[0]-w/2, self.b)
                        draw.text(coords, text, font=self.font, fill="white")

                