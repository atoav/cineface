# cineface

Cineface is a Hardware OSC Controller for the RME Totalmix outputs. It is planned to have:
- 5x LED Button (L/R, Center, Lfe, Ls/Rs, Headphones) for muting
- 1x Motorpotentiometer, for global volume control
- 2x OLED Displays, one for displaying the dB value and one for displaying the current peak levels of the channels

It is meant to run on a raspberry pi 3 and look a bit like this:



![](images/panel.png)



## Current State of Affairs

- [x] Receiving OSC from TotalMix (reacting to UI change) via Network
- [x] Sending OSC to TotalMix (remotely changing the UI) via Network
- [x] Button/LED Implementation
- [ ] db-Display Implementation
- [ ] levels-Display Implementation
- [ ] Potentiometer (ADC) Implementation
- [ ] Potentiometer (Motor) Implementation
- [ ] Building a Case



## Raspi Pinout

| Pin  |      |      |
| ---- | ---- | ---- |
|      |      |      |
|      |      |      |
|      |      |      |



## Switches

I use switches with a two-terminal bicolor LED inside (red/green). I am only going to use the green part to display whether a channel is unmuted (green) or muted (off). However one could also use both colors from a raspi as follows (e.g. to indicate clipping):

![](images/led_drives.png)

For the switches I am using the raspi internal pull-up-resistor.

## Motor Potentiometer

A motor Potentiometer is a potentiometer coupled to a motor. This means we can read out the current dial position of the potentiometer using an ADC and set the Volume of TotalMix accordingly. Should we change the volume in the TotalMix UI or load up a different snapshot we can use the motor to move the dial into a position where it represents the GUI volume again. This means the motor potentiometer consists of two parts:

### 1. Driving the motor

Drive motor with H-Bridge (for Simulation [see here](https://tinyurl.com/yc7tqva5)):

![](images/h-bridge.png)

Or use an chip like the [L293](https://www.ti.com/product/L293) see instructions for how to use it with a raspi [here](https://www.instructables.com/DC-Motor-Control-With-Raspberry-Pi-and-L293D/).

### 2. Reading out the dial

I decided on using a MCP3001 which is a 1-channel 10bit ADC with SPI connector



## Displays



