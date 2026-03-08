import gdsfactory as gf
from gdsfactory.typings import Layer


class LAYER(gf.technology.LayerMap):
    WG: Layer = (1, 0)
    SLAB: Layer = (2, 0)
    P: Layer = (3, 0)
    N: Layer = (4, 0)
    PPP: Layer = (7, 0)
    NPP: Layer = (8, 0)
    M1: Layer = (21, 0)
    M2: Layer = (22, 0)
    BOX: Layer = (30, 0)
    CLAD: Layer = (31, 0)
    WAFER: Layer = (32, 0)
