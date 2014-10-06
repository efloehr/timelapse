def rgb_to_int(rgb_tuple):
    return int(round(rgb_tuple[0]*256*256 + rgb_tuple[1]*256 + rgb_tuple[2]))

def int_to_rgb(rgb_int):
    r = (rgb_int >> 16) & 255
    g = (rgb_int >> 8) & 255
    b = rgb_int & 255
    return (r,g,b)

