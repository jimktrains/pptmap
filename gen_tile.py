#!/usr/bin/env python

import os, os.path
import mapnik
import math
from globalmaptiles import GlobalMercator
from globalmaptiles import GlobalGeodetic

def get_renderers(path, zmax = 20):
    r = {}
    for filename in os.listdir(path):
        print filename
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
        self.m = mapnik.Map(2*self.sx, 2*self.sy)
        self.max_zoom = max_zoom
        self.gprj = GlobalMercator()
        try:
            mapnik.load_map(self.m,mapfile)
        except RuntimeError as e:
            print e
            raise ValueError("Bad file", mapfile)

    def genTile(self, x, y, z, ext="png", cache=False):
        outname = os.tmpnam()

        print "x=", x, "y=", y, "z=", z

        (minLat, minLon, maxLat, maxLon) = self.gprj.TileLatLonBounds(x,y,z)
        bbox = mapnik.Envelope(minLon, minLat, maxLon, maxLat)
        print bbox
        bbox.width(bbox.width() * 2)
        bbox.height(bbox.height() * 2)
        self.m.zoom_to_box(bbox)

        im = mapnik.Image(self.sx*2, self.sy*2)
        mapnik.render(self.m, im)
        view = im.view(self.sx/2, self.sy/2, self.sx, self.sy)
        
        view.save(outname, ext)
        
        fd = open(outname)
        out = fd.read()
        fd.close()

        if not cache:
            os.unlink(outname)
        return out
