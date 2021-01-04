#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image

from cineface.totalmix import db_to_fader, fader_to_db




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
        self.active     = False
        self.serial     = None
        self.device     = None
        self.font       = None
        self.font_small = None
        self.db_markers = None
        self.scale      = None

        # Some geometric constants
        # Width and height of screen
        self.h = 64
        self.w = 128

        # minimum height of a meter bar (so it doesn't vanish)
        self.min_height = 2

        # Number of horizontal slots
        self.slots      = 9
        self.slotwidth  = 128/self.slots

        # Margins
        self.margin_bottom = 10
        self.margin_top    = 0

        # Bottom column
        self.b = self.h - self.margin_bottom

        # Height and Width of bar, space between them
        self.barheight = self.h - self.margin_bottom - self.margin_top
        self.barwidth  = 8
        self.gutter    = (self.slotwidth-self.barwidth)/2

        # find Zero dB point
        self.zerodb = db_to_fader(0.0)

        # Horizontal offset for dB scale labels
        self.db_offset = -6

        self.db_line_dash_spacing = 4
        self.db_line_dash_width   = 1

        # Scale the bar up to zero db (so we don't waste vertical space)
        self.barheight = self.barheight / self.zerodb

    def from_config(self, config) -> 'LevelDisplay':
        # Temporary Variables
        active       = config["LevelDisplay"]["active"]
        address      = config["LevelDisplay"]["i2c_address"]
        port         = config["LevelDisplay"]["i2c_port"]
        left         = config["LevelDisplay"]["left"]
        right        = config["LevelDisplay"]["right"]
        if "db_markers" in config["LevelDisplay"].keys():
            db_markers = config["LevelDisplay"]["db_markers"]
            scale      = [db_to_fader(db) for db in db_markers]
        else:
            db_markers = None

        # Set the initial values
        self.active = active
        if self.active:
            self.serial     = i2c(port=port, address=address)
            self.device     = sh1106(self.serial)
            self.font       = ImageFont.truetype("fonts/Inter-Medium.ttf", 10)
            self.font_small = ImageFont.truetype("fonts/Inter-Light.ttf", 7)
            self.left       = left
            self.right      = right
            self.db_markers = db_markers
            self.scale      = scale

            print("Setting up LevelDisplay at i2c address {}".format(address))

        return self


    def draw_scale(self, draw, slot):
        """
        Draw a dB scale
        """
        for i, value in enumerate(self.scale):
            # get the y coordinate
            y = self.b+value*-self.barheight

            # Draw a dotted bar
            draw.line([(0, y), (self.w, y)], fill="white")
            if not self.db_line_dash_spacing == 0:
                for x in range(0, self.w, self.db_line_dash_spacing):
                    dash_width = self.db_line_dash_spacing - self.db_line_dash_width -1
                    draw.rectangle([(x, y-1), (x+dash_width, y+1)], fill="black")

            # Get the value in dB and format the labels
            db = self.db_markers[i]
            text = "{:.0f}".format(db)

            # Get the text width
            w, h = draw.textsize(text, self.font_small)

            # If the label is on the very top, push it down
            if y-h/2 < 0:
                y = y+h/2

            # If the label is on the very bottom, push it up
            if y+h/2 > self.b:
                y = y-h/2

            # Construct coordinates for the label
            center = (slot*self.slotwidth+self.db_offset, y-h/2)
            coords = (center[0]-w/2, y-h/2)

            # Draw black rectangle and text
            draw.rectangle([(coords[0]-3, coords[1]), (center[0]+w/2+3, y+h/2)], outline="black", fill="black")
            draw.text(coords, text, font=self.font_small, fill="white")



    def draw(self, outputs):
        # if inactive just return
        if not self.active:
            return

        # Draw on canvas
        with canvas(self.device) as draw:

            # Draw the dB scale if there are values in the config
            if not self.db_markers is None:
                # Get a count of right channels to position the db bar so we can position the value labels
                n_right = sum([2 for o in outputs if o.name is not None and o.name in self.right and o.stereo])
                n_right += sum([1 for o in outputs if o.name is not None and o.name in self.right and o.mono])

                self.draw_scale(draw, self.slots-n_right)

            n = 0
            # Draw the left aligned outputs first
            for output in [o for o in outputs if o.name is not None and o.name in self.left]:
                # If the outputs aren't ready yet just skip drawing them
                if output.stereo and (output.levels["L"] is None or output.levels["R"] is None or output.mute is None):
                    continue

                # Do the same for mono outputs
                if output.mono and (output.levels is None or output.mute is None):
                    continue

                # Draw level meter bars
                if output.stereo:
                    # Stereo channels take up two slots
                    draw.rectangle([(n*self.slotwidth, self.b+output.levels["L"]*-self.barheight), (n*self.slotwidth+self.barwidth, self.b)], outline="white", fill="white")
                    n += 1
                    draw.rectangle([(n*self.slotwidth, self.b+output.levels["R"]*-self.barheight), (n*self.slotwidth+self.barwidth, self.b)], outline="white", fill="white")
                    n += 1
                else:
                    # Mono channels take up one slot
                    draw.rectangle([(n*self.slotwidth, self.b+output.levels*-self.barheight), (n*self.slotwidth+self.barwidth, self.b)], outline="white", fill="white")
                    n += 1

                # Draw Channel Names and Mute icons
                if output.mute and output.mono:
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
                elif output.mono:
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
                    draw.rectangle([(self.w-(n*self.slotwidth), self.b+output.levels["R"]*-self.barheight), (self.w-(n*self.slotwidth+self.barwidth), self.b)], outline="white", fill="white")
                    n += 1
                    draw.rectangle([(self.w-(n*self.slotwidth), self.b+output.levels["L"]*-self.barheight), (self.w-(n*self.slotwidth+self.barwidth), self.b)], outline="white", fill="white")
                    n += 1
                else:
                    draw.rectangle([(self.w-(n*self.slotwidth), self.b+output.levels*-self.barheight), (self.w-(n*self.slotwidth+self.barwidth), self.b)], outline="white", fill="white")
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

                