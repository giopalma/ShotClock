import colorsys


def hex_to_rgb(color: str):
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return (r, g, b)


def hex_to_hsv(color: str):
    r, g, b = hex_to_rgb(color)
    return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)


def hsv_to_opencv_hsv(hsv: tuple):
    h, s, v = hsv
    return int(h * 179), int(s * 255), int(v * 255)


def hex_to_opencv_hsv(color: str):
    hsv = hex_to_hsv(color)
    return hsv_to_opencv_hsv(hsv)


class CircularArray:
    def __init__(self, size):
        self.size = size
        self.array = []

    def add(self, element):
        if len(self.array) >= self.size:
            self.array.pop(0)
        self.array.append(element)

    def get_array(self):
        return self.array

    def get_len(self):
        return len(self.array)
