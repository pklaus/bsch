valid = ["Rainbow", "RainbowHM", "Iron", "Greyscale"]

def colormaps():
    return valid

# A helper function related the colormap handling in matplotlib:

def get_cmap(name, lut=None):
    """
    Return the colormap with that name.
    Modeled after matplotlib.cm.get_cmap() but for the colormaps defined here.

    Raises ValueError if not found.
    """
    if name not in colormaps():
        raise ValueError(f"'{name}' is not a valid value for name; supported values are {', '.join(colormaps())}")
    cls = globals().get(name)
    return cls.create_mpl_cmap(N=lut or 256)

# The abstract Colormap class:

class Colormap:

    int_cdict = None
    name = None

    @classmethod
    def float_cdict(cls):
        cdict = {"red": [], "green": [], "blue": []}
        for color, stops in cls.int_cdict.items():
            for x, y0, y1 in stops:
                cdict[color].append((x / 1023.0, y0 / 255.0, y1 / 255.0))
        return cdict

    @classmethod
    def create_mpl_cmap(cls, N=256, gamma=1.0):
        import matplotlib.colors

        cdict = cls.float_cdict()
        return matplotlib.colors.LinearSegmentedColormap(
            cls.name, cdict, N=N, gamma=gamma
        )

# The individual colormaps:

class Greyscale(Colormap):
    name = "Greyscale"
    int_cdict = {
        "blue": [(0, 0, 0), (1023, 255, 255)],
        "green": [(0, 0, 0), (1023, 255, 255)],
        "red": [(0, 0, 0), (1023, 255, 255)],
    }


class Rainbow(Colormap):
    name = "Rainbow"
    int_cdict = {
        "blue": [
            (0, 196, 196),
            (256, 255, 255),
            (511, 0, 0),
            (767, 0, 0),
            (1023, 0, 0),
        ],
        "green": [
            (0, 0, 0),
            (256, 255, 255),
            (511, 157, 157),
            (767, 255, 255),
            (1023, 0, 0),
        ],
        "red": [(0, 0, 0), (256, 0, 0), (511, 0, 0), (767, 255, 255), (1023, 255, 255)],
    }


class RainbowHM(Colormap):
    name = "RainbowHM"
    int_cdict = {
        "blue": [
            (0, 0, 0),
            (143, 210, 210),
            (296, 240, 240),
            (440, 1, 1),
            (583, 14, 14),
            (732, 0, 0),
            (880, 0, 0),
            (1023, 254, 254),
        ],
        "green": [
            (0, 0, 0),
            (143, 1, 1),
            (296, 239, 239),
            (440, 134, 134),
            (583, 231, 231),
            (732, 131, 131),
            (880, 1, 1),
            (1023, 254, 254),
        ],
        "red": [
            (0, 0, 0),
            (143, 0, 0),
            (296, 8, 8),
            (440, 0, 0),
            (583, 241, 241),
            (732, 255, 255),
            (880, 255, 255),
            (1023, 255, 255),
        ],
    }


class Iron(Colormap):
    name = "Iron"
    int_cdict = {
        "blue": [
            (0, 0, 0),
            (71, 103, 103),
            (315, 175, 175),
            (335, 163, 163),
            (511, 44, 44),
            (695, 0, 0),
            (868, 55, 55),
            (874, 61, 61),
            (1023, 255, 255),
        ],
        "green": [
            (0, 0, 0),
            (71, 0, 0),
            (315, 0, 0),
            (335, 4, 4),
            (511, 44, 44),
            (695, 126, 126),
            (868, 229, 229),
            (874, 231, 231),
            (1023, 255, 255),
        ],
        "red": [
            (0, 0, 0),
            (71, 5, 5),
            (315, 183, 183),
            (335, 188, 188),
            (511, 224, 224),
            (695, 255, 255),
            (868, 255, 255),
            (874, 255, 255),
            (1023, 255, 255),
        ],
    }
