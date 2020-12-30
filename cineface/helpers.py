#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def clamp(n, minn, maxn):
    """
    Clamp a value to a range (limit it to the range)
    """
    return max(min(maxn, n), minn)


def lerp(value, start, end, minimum=0.0, maximum=1.0):
    """
    Linear Interpolation between two points, clamping it to the minimum/maximum
    """
    value = float(value)
    start = float(start)
    end = float(end)
    return clamp(((1.0-value) * start +value * end), minimum, maximum)


def fit(value, min1, max1, min2, max2):
    """
    Scale and translate a value from one range to another range
    """
    # Figure out how 'wide' each range is
    span1 = max1 - min1
    span2 = max2 - min2

    # Convert the left range into a 0-1 range (float)
    scaled = float(value - min1) / float(span1)

    # Convert the 0-1 range into a value in the right range.
    return min2 + (scaled * span2)

def nothing():
    """
    Do nothing
    """
    pass