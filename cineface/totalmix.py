#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cineface.helpers import fit, clamp, lerp

# db to fadercurve lookup table (pulled by sweeping fader via code)
FADER_CURVE = [
    (-65.0, 0.0),
    (-63.5, 0.00999998115003109),
    (-62.0, 0.020000021904706955),
    (-60.5, 0.030000003054738045),
    (-59.0, 0.039999984204769135),
    (-57.6, 0.05000002309679985),
    (-56.2, 0.06000000610947609),
    (-54.7, 0.06999998539686203),
    (-53.4, 0.07999996840953827),
    (-52.0, 0.09000000357627869),
    (-50.6, 0.09000000357627869),
    (-49.3, 0.10999996960163116),
    (-48.0, 0.1199999526143074),
    (-46.7, 0.12999999523162842),
    (-45.4, 0.13999997079372406),
    (-44.2, 0.15000000596046448),
    (-42.9, 0.1599999964237213),
    (-41.7, 0.16999997198581696),
    (-40.5, 0.18000000715255737),
    (-39.3, 0.1899999976158142),
    (-38.2, 0.20000003278255463),
    (-37.0, 0.21000002324581146),
    (-35.9, 0.2199999988079071),
    (-34.8, 0.22999997437000275),
    (-33.7, 0.24000002443790436),
    (-32.6, 0.25),
    (-31.6, 0.25999999046325684),
    (-30.6, 0.27000001072883606),
    (-29.5, 0.2800000011920929),
    (-28.6, 0.28999999165534973),
    (-27.6, 0.30000001192092896),
    (-26.6, 0.3099999725818634),
    (-25.7, 0.3199999928474426),
    (-24.8, 0.33000001311302185),
    (-23.9, 0.3400000035762787),
    (-23.0, 0.3499999940395355),
    (-22.1, 0.36000001430511475),
    (-21.3, 0.3700000047683716),
    (-20.5, 0.3799999952316284),
    (-19.7, 0.3799999952316284),
    (-18.9, 0.4000000059604645),
    (-18.1, 0.4099999666213989),
    (-17.4, 0.41999998688697815),
    (-16.7, 0.429999977350235),
    (-16.0, 0.4399999976158142),
    (-15.3, 0.44999998807907104),
    (-14.6, 0.46000000834465027),
    (-14.0, 0.4699999988079071),
    (-13.3, 0.47999998927116394),
    (-12.7, 0.49000000953674316),
    (-12.1, 0.5),
    (-12.0, 0.502),
    (-11.6, 0.5099999904632568),
    (-11.0, 0.5199999213218689),
    (-10.5, 0.5299999713897705),
    (-9.9, 0.5400000214576721),
    (-9.4, 0.550000011920929),
    (-9.0, 0.5600000023841858),
    (-8.5, 0.5699999928474426),
    (-8.1, 0.5799999833106995),
    (-7.6, 0.5899999141693115),
    (-7.2, 0.6000000238418579),
    (-6.9, 0.6100000143051147),
    (-6.5, 0.6200000047683716),
    (-6.1, 0.6299999952316284),
    (-6.0, 0.634),
    (-5.8, 0.6399999260902405),
    (-5.5, 0.6499999165534973),
    (-5.2, 0.6600000262260437),
    (-4.8, 0.6699999570846558),
    (-4.5, 0.6799999475479126),
    (-4.2, 0.6899999380111694),
    (-3.8, 0.6999999284744263),
    (-3.5, 0.7099999189376831),
    (-3.2, 0.7200000286102295),
    (-2.9, 0.7299999594688416),
    (-2.5, 0.7399999499320984),
    (-2.2, 0.7499999403953552),
    (-1.9, 0.7599999308586121),
    (-1.5, 0.7699999213218689),
    (-1.2, 0.7799999117851257),
    (-0.9, 0.7899999618530273),
    (-0.6, 0.7999999523162842),
    (-0.2, 0.809999942779541),
    (0.0, 0.817),
    (0.1, 0.8199999332427979),
    (0.4, 0.8299999237060547),
    (0.7, 0.8399999141693115),
    (1.1, 0.8499999642372131),
    (1.4, 0.85999995470047),
    (1.7, 0.8699999451637268),
    (2.1, 0.8799999356269836),
    (2.4, 0.8899999260902405),
    (2.7, 0.8999999165534973),
    (3.0, 0.909),
    (3.4, 0.9199999570846558),
    (3.7, 0.9299999475479126),
    (4.0, 0.9399999380111694),
    (4.4, 0.9499999284744263),
    (4.7, 0.9599999189376831),
    (5.0, 0.9699999690055847),
    (5.3, 0.9799999594688416),
    (5.7, 0.9899999499320984),
    (6.0, 1.0),
]


def db_to_fader(x):
    """
    Transform a db value to a fader value
    This is essentially a linear interpolation between the meassured points
    stored in FADER_CURVE
    """
    x = clamp(x, FADER_CURVE[0][0], FADER_CURVE[-1][0])
    
    # If the value is in the list return it directly
    if x in [db for (db, fader) in FADER_CURVE]:
        i = [db for (db, fader) in FADER_CURVE].index(x)
        return FADER_CURVE[i][1]
    
    # Find the next smaller value (or use the smallest one)
    if x != FADER_CURVE[0][0]:
        next_smaller = max([(db, fader) for (db, fader) in FADER_CURVE if db < x])
    else:
        next_smaller = FADER_CURVE[0]
        
    # Find the next bigger value (or use the smallest one)
    if x != FADER_CURVE[-1][0]:
        next_bigger = min([(db, fader) for (db, fader) in FADER_CURVE if db > x])
    else:
        next_bigger = FADER_CURVE[-1]
    # On a range of 0.0 to 1.0, how far has x traveled between
    # next_smaller and next_bigger?
    factor = 1-(1/(next_smaller[0]-next_bigger[0]))*(x-next_bigger[0])
    
    # Linearily interpolate between the values
    blended_value = lerp(factor, next_smaller[1], next_bigger[1])
    
    return blended_value


def fader_to_db(x):
    """
    Transform a fader value to a db value
    This is essentially a linear interpolation between the meassured points
    stored in FADER_CURVE
    """
    x = clamp(x, FADER_CURVE[0][1], FADER_CURVE[-1][1])
    
    # If the value is in the list return it directly
    if x in [fader for (db, fader) in FADER_CURVE]:
        i = [fader for (db, fader) in FADER_CURVE].index(x)
        return FADER_CURVE[i][0]
    
    # Find the next smaller value (or use the smallest one)
    if x != FADER_CURVE[0][1]:
        next_smaller = max([(db, fader) for (db, fader) in FADER_CURVE if fader < x])
    else:
        next_smaller = FADER_CURVE[0]
        
    # Find the next bigger value (or use the smallest one)
    if x != FADER_CURVE[-1][1]:
        next_bigger = min([(db, fader) for (db, fader) in FADER_CURVE if fader > x])
    else:
        next_bigger = FADER_CURVE[-1]
    # On a range of 0.0 to 1.0, how far has x traveled between
    # next_smaller and next_bigger?
    factor = 1-(1/(next_smaller[1]-next_bigger[1]))*(x-next_bigger[1])
    
    # Linearily interpolate between the values
    blended_value = lerp(factor, next_smaller[0], next_bigger[0], minimum=FADER_CURVE[0][0], maximum=FADER_CURVE[-1][0])
    
    return blended_value  




class Output():
    """
    Represents a single RME Totalmix Output channel
    """
    def __init__(self, name: str, address: str, stereo=False, gpio_button=None, gpio_led=None):
        # Name is an arbitrary string for reference
        self.name = name

        # Address is the OSC Address (e.g. /1/volume4)
        self.address = address

        # Stores the current position of the volume (0.0 to 1.0)
        self.volume = None

        # Stores the current mute state
        self.mute = None

        # Outputs can be either Stereo or Mono
        self.stereo = stereo

        # Stores the bin of the corresponding button
        self.gpio_button = gpio_button

        # Stores the bin of the corresponding led
        self.gpio_led = gpio_led

        # Levels store the current meter value (must be enabled in Totalmix
        # OSC preferences). This is either a single float or a dict, depending
        # on the number of channels
        if self.stereo:
            self.levels = {
                "L" : None,
                "R" : None
            }
        else:
            self.levels = None

        # Stores the string for the display value (e.g. "6 dB" or "-oo")
        self.display_value = None


    def as_table(self) -> str:
        label = "{}:".format(self.name)
        volume = "{}".format(self.display_value)
        if self.stereo:
            levels = "{}/{}".format(self.levels["L"], self.levels["R"])
        else:
            levels = "{}".format(self.levels)

        if self.mute:
            mute = "MUTE"
        else:
            mute = "-"
        return "{:>15} {:>15} {:>15} {:^15}".format(label, volume, levels, mute)

    def __str__(self):
        return "Output ({} @ {}): volume={} ({}), levels={}".format(self.name, self.address, self.volume, self.display_value, self.levels)

    def __repr__(self):
        return self.address

    @property
    def number(self) -> int:
        """
        Returns the number of the channel (e.g. 4)
        """
        return int(self.address[-1])

    @property
    def address_display(self) -> str:
        """
        Returns the OSC display address (e.g. "/1/volume4Val")
        """
        return "{}Val".format(self.address)

    @property
    def address_levels(self):
        """
        Returns the OSC meter levels address (e.g. ["/1/level4Left"] for a mono
        output or ["/1/level4Left", "/1/level4Right"] for a stereo output)
        """
        # base adress
        base = "/1/level{}".format(self.number)

        # If stereo return a list with address for left/right, for mono
        # outputs return only left channel
        if self.stereo:
            return ["{}Left".format(base), "{}Right".format(base)]
        else:
            return ["{}Left".format(base)]

    @property
    def address_mute(self):
        """
        Returns the OSC mute address (e.g. "/1/mute/1/4")
        """
        return "/1/mute/1/{}".format(self.number)

    def is_valid_address(self, addr) -> bool:
        """
        Check if the given address belongs to this output
        """
        return addr == self.address or addr == self.address_display or addr == self.address_mute or addr in self.address_levels

    def update(self, addr, value):
        """
        Update all values with the ones coming from TotalMix
        """
        if addr == self.address:
            self.volume = value
        elif addr == self.address_display:
            self.display_value = value
        elif addr == self.address_mute:
            self.mute = value == 1.0
        elif addr in self.address_levels:
            if self.stereo:
                if addr.endswith("Left"):
                    self.levels["L"] = value
                elif addr.endswith("Right"):
                    self.levels["R"] = value
            else:
                if addr.endswith("Left"):
                    self.levels = value

    def set_volume(self, client, volume: float):
        """
        Set the volume of the output to a value between 0.0 and 1.0
        """
        # Select output bus
        client.send_message("/setBankStart", 1.0)
        client.send_message("/1/busOutput", 1.0)

        # Clamp volume to range witrhin 0.0 and 1.0
        volume = clamp(volume, 0.0, 1.0)

        # Send message
        client.send_message(self.address, volume)

    def set_mute(self, client):
        """
        Mute the output
        """
        # Select output bus
        client.send_message("/setBankStart", 1.0)
        client.send_message("/1/busOutput", 1.0)

        # Send mute message
        client.send_message(self.address_mute, 1.0)

    def set_unmute(self, client):
        """
        Mute the output
        """
        # Select output bus
        client.send_message("/setBankStart", 1.0)
        client.send_message("/1/busOutput", 1.0)

        # Send unmute message
        client.send_message(self.address_mute, 0.0)

    def toggle_mute(self, client):
        """
        Mute the output if it was unmuted before
        Unmute the output if it was muted before
        """
        # Select output bus
        client.send_message("/setBankStart", 1.0)
        client.send_message("/1/busOutput", 1.0)

        # Send mute/unmute message depending on previous state
        if self.mute:
            client.send_message(self.address_mute, 1.0)
        else:
            client.send_message(self.address_mute, 0.0)




class Outputs():
    """
    Represents a collection of RME Output Channels
    """
    def __init__(self):
        self.faders = []
        self.pre_mute_states = []
        self.pre_solo_states = []
        self.solo_active = False

    def __iter__(self):
        for output in self.faders:
            yield output

    def from_config(self, config) -> 'Outputs':
        for output in config["Output"]:
            o = Output(
                name=output["name"],
                address=output["address"],
                stereo=output["stereo"],
                gpio_button=output["gpio_button"],
                gpio_led=output["gpio_led"]
            )
            self.faders.append(o)

        return self

    def mute_all(self, client):
        """
        Mute all output channels and store the formerly muted state.
        After this you can either run undo_mute_all() or unmute_all(),
        depending on the state you want to return back to
        """
        # Run only if not all muted already
        if not all([o.mute for o in self.faders]):
            for i, output in enumerate(self.faders):
                # Frist save previous state
                self.pre_mute_states[i] = output.mute

                # Second mute the output
                output.set_mute(client)

    def undo_mute_all(self, client):
        """
        Undo mute_all and return back to the state before (formerly muted outputs
        will remain muted, formerly unmuted ones will be unmuted again)
        """
        for i, output in enumerate(self.faders):
            # Unmute Outputs only if they have been previously unmuted
            if self.pre_mute_states[i]:
                output.set_unmute(client)

    def unmute_all(self, client):
        """
        Unmute all output channels (regardless of previous state)
        """
        for output in self.faders:
            output.set_unmute(client)

    def invert_mutes(self, client):
        """
        Unmute all muted Tracks, mute all unmuted ones
        """
        for output in self.faders:
            output.toggle_mute(client)

    def dim(self, client):
        """
        Dim the volume of all outputs by -6db
        """
        for i, output in enumerate(self.faders):
            output.set_volume(client, output.volume * 0.7746)

    def undim(self, client):
        """
        Raise the volume of all outputs by +6db
        """
        for i, output in enumerate(self.faders):
            output.set_volume(client, output.volume * 1/0.7746)

    def silence(self, client):
        """
        Set all outputs to 0.0
        """
        for i, output in enumerate(self.faders):
            output.set_volume(client, 0.0)