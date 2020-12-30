#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
from gpiozero import Button, LED
from datetime import datetime
import sys
sys.path.append(".")

from cineface.helpers import nothing

class LedButton():
    def __init__(self, button_pin, led_pin, mute, unmute):
        self.button_pin = button_pin
        self.led_pin = led_pin
        self.mute = mute
        self.unmute = unmute
        self.button = Button(self.button_pin, pull_up=True, bounce_time=0.01, hold_time=1.5)
        print("Setting up Button (Pin: {})".format(self.button_pin))
        self.button.when_pressed = self.pressed
        self.led = LED(self.led_pin)

    def __cmp__(self, other):
        return self.button_pin == other.button_pin

    def pressed(self):
        """
        Fired if button was pressed and not held
        """
        print("Pressed (Pin: {}): {} -- {}".format(self.button_pin, datetime.now(), self))
        if self.led.is_lit:
            self.led.off()
            self.mute()
        else:
            self.led.on()
            self.unmute()
    
    def update_led(self, mute):
        if mute:
            self.led.off()
        else:
            self.led.on()


