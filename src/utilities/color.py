from typing import List, Union

import cv2
import numpy as np


class Color:
    def __init__(self, lower: List[int], upper: List[int] = None):
        """
        Defines a color or range of colors. This class converts RGB colors to BGR to satisfy OpenCV's color format.
        Args:
            lower: The lower bound of the color range [R, G, B].
            upper: The upper bound of the color range [R, G, B]. Exclude this arg if you're defining a solid color.
        """
        self.lower = np.array(lower[::-1])
        self.upper = np.array(upper[::-1]) if upper else np.array(lower[::-1])


def isolate_colors(image: cv2.Mat, colors: Union[Color, List[Color]]) -> cv2.Mat:
    """
    Isolates ranges of colors within an image and saves a new resulting image.
    Args:
        image: The image to process.
        colors: A Color or list of Colors.
    Returns:
        The image with the isolated colors (all shown as white).
    """
    if not isinstance(colors, list):
        colors = [colors]
    # Generate masks for each color
    masks = [cv2.inRange(image, color.lower, color.upper) for color in colors]
    # Create black mask
    h, w = image.shape[:2]
    mask = np.zeros([h, w, 1], dtype=np.uint8)
    # Combine masks
    for mask_ in masks:
        mask = cv2.bitwise_or(mask, mask_)
    return mask


"""Solid colors"""
# Define colors with their ranges
BLACK = Color([0, 0, 0], [50, 50, 50])
BLUE = Color([0, 0, 200], [0, 0, 255])
CYAN = Color([0, 200, 200], [0, 255, 255])
GREEN = Color([0, 200, 0], [0, 255, 0])
ORANGE = Color([200, 100, 0], [255, 165, 80])
PINK = Color([200, 0, 200], [255, 100, 255])
PURPLE = Color([100, 0, 200], [180, 0, 255])
RED = Color([200, 0, 0], [255, 80, 80])
WHITE = Color([200, 200, 200], [255, 255, 255])
YELLOW = Color([200, 200, 0], [255, 255, 100])

"""Colors for use with semi-transparent text"""
OFF_CYAN = Color([0, 200, 200], [70, 255, 255])
OFF_GREEN = Color([0, 100, 0], [30, 255, 255])
OFF_ORANGE = Color([180, 100, 30], [255, 166, 103])
OFF_WHITE = Color([190, 190, 190], [255, 255, 255])
OFF_YELLOW = Color([190, 190, 0], [255, 255, 120])

"""Colors for use with minimap orb text"""
ORB_GREEN = Color([0, 255, 0], [255, 255, 0])
ORB_RED = Color([255, 0, 0], [255, 255, 0])

# Defines if in altar
IN_ALTAR = Color([0, 185, 0], [0, 195, 0])
POOL = Color([178, 0, 0], [188, 0, 0])
CLIMB = Color([167, 0, 0], [177, 0, 0])
START = Color([155, 0, 0], [166, 0, 0])
BARRIER = Color([144, 0, 0], [154, 0, 0])
STARTING = Color([0, 170, 0], [0, 180, 0])

# Portals
WEST = Color([0, 100, 0], [0, 110, 0])
SOUTHWEST = Color([0, 111, 0], [0, 121, 0])
SOUTH = Color([0, 122, 0], [0, 132, 0])
SOUTHEAST = Color([0, 133, 0], [0, 143, 0])
EAST = Color([0, 144, 0], [0, 154, 0])


# Define 12 colors within the RED range (BGR format)
MIND_PILLAR = Color([200, 0, 0], [210, 6, 6])  # Specific color: [205, 3, 3], Mind Altar
AIR_PILLAR = Color([211, 7, 7], [221, 13, 13])  # Specific color: [216, 10, 10], Air Altar
COSMIC_PILLAR = Color([222, 14, 14], [232, 20, 20])  # Specific color: [227, 17, 17], cosmic
WATER_PILLAR = Color([233, 21, 21], [243, 27, 27])  # Specific color: [238, 24, 24], water
EARTH_PILLAR = Color([244, 28, 28], [254, 34, 34])  # Specific color: [249, 31, 31], earth 
NATURE_PILLAR = Color([255, 35, 35], [255, 41, 41])  # Specific color: [255, 38, 38], nature
FIRE_PILLAR = Color([255, 42, 42], [255, 48, 48])  # Specific color: [255, 45, 45], fire
BLOOD_PILLAR = Color([255, 49, 49], [255, 55, 55])  # Specific color: [255, 52, 52], blood
LAW_PILLAR = Color([255, 56, 56], [255, 62, 62])  # Specific color: [255, 59, 59], law
DEATH_PILLAR = Color([255, 63, 63], [255, 69, 69])  # Specific color: [255, 66, 66], death
CHAOS_PILLAR = Color([255, 70, 70], [255, 76, 76])  # Specific color: [255, 73, 73], chaos
BODY_PILLAR = Color([255, 77, 77], [255, 80, 80])  # Specific color: [255, 78, 78], body

COLOR_1 = Color([50, 0, 0], [60, 0, 0])
COLOR_2 = Color([61, 0, 0], [71, 0, 0])
COLOR_3 = Color([72, 0, 0], [82, 0, 0])
COLOR_4 = Color([83, 0, 0], [93, 0, 0])
COLOR_5 = Color([94, 0, 0], [104, 0, 0])
COLOR_6 = Color([105, 0, 0], [115, 0, 0])
COLOR_7 = Color([116, 0, 0], [126, 0, 0])
COLOR_8 = Color([127, 0, 0], [137, 0, 0])
COLOR_9 = Color([138, 0, 0], [148, 0, 0])
COLOR_10 = Color([149, 0, 0], [159, 0, 0])
COLOR_11 = Color([160, 0, 0], [170, 0, 0])
COLOR_12 = Color([171, 0, 0], [181, 0, 0])
COLOR_13 = Color([182, 0, 0], [192, 0, 0])
COLOR_14 = Color([193, 0, 0], [203, 0, 0])
COLOR_15 = Color([204, 0, 0], [214, 0, 0])
COLOR_16 = Color([215, 0, 0], [225, 0, 0])
COLOR_17 = Color([226, 0, 0], [236, 0, 0])
COLOR_18 = Color([237, 0, 0], [242, 0, 0])
COLOR_19 = Color([243, 0, 0], [249, 0, 0])
COLOR_20 = Color([250, 0, 0], [255, 0, 0])
