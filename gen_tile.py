#!/usr/bin/env python

import os, os.path
import mapnik
import math
from globalmaptiles import GlobalMercator
from globalmaptiles import GlobalGeodetic

def get_renderers(path, zmax = 20):
    r = {}
    for filename in os.listdir(path):
        if filename.startswith("."):
            continue
        if not filename.endswith(".xml"):
            continue
        rname = filename[:-4]
        r[rname] = MapMaker(os.path.join(path, filename), zmax)
    return r

class MapMaker:
    sx = 256
    sy = 256
    prj = mapnik.Projection("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    def __init__(self, mapfile, max_zoom):
        self.m = mapnik.Map(self.sx, self.sy)
        self.max_zoom = max_zoom
        self.gprj = GlobalMercator();
        try:
            mapnik.load_map(self.m,mapfile)
        except RuntimeError as e:
            print e
            raise ValueError("Bad file", mapfile)

    def genTile(self, x, y, z, ext="png", cache=False):
        outname = os.tmpnam()

        (minLat, minLon, maxLat, maxLon) = self.gprj.TileLatLonBounds(x,y,z)
        bbox = mapnik.Envelope(minLon, minLat, maxLon, maxLat)

        self.m.aspect_fix_mode = mapnik.aspect_fix_mode.ADJUST_CANVAS_WIDTH
        self.m.zoom_to_box(bbox)

        im = mapnik.Image(self.m.width, self.m.height)
        mapnik.render(self.m, im)

        view = im.view(0,0,self.m.width, self.m.height)
        view.save(outname, ext)
        
        fd = open(outname)
        out = fd.read()
        fd.close()

        if not cache:
            os.unlink(outname)
        return out
