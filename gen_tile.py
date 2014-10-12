#!/usr/bin/env python

import os, os.path
import mapnik
import math

def minmax (a,b,c):
    a = max(a,b)
    a = min(a,c)
    return a


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



class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * math.pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2
                
    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = minmax(math.sin(math.radians(ll[1])),-0.9999,0.9999)
         g = round(d[1] + 0.5*math.log((1+f)/(1-f))*-self.Cc[zoom])
         return (e,g)
     
    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0])/self.Bc[zoom]
         g = (px[1] - e[1])/-self.Cc[zoom]
         h = math.degrees( 2 * math.atan(math.exp(g)) - 0.5 * math.pi)
         return (f,h)

class MapMaker:
    sx = 256
    sy = 256
    prj = mapnik.Projection("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    def __init__(self, mapfile, max_zoom):
        self.m = mapnik.Map(2*self.sx, 2*self.sy)
        self.max_zoom = max_zoom
        self.gprj = GoogleProjection(max_zoom)
        try:
            mapnik.load_map(self.m,mapfile)
        except RuntimeError as e:
            print e
            raise ValueError("Bad file", mapfile)
        self.name = hex(hash(mapfile))

    def tileno2bbox(self, x, y, z):
        p0 = self.gprj.fromPixelToLL((self.sx*x, self.sy*(y+1)), z)
        p1 = self.gprj.fromPixelToLL((self.sx*(x+1), self.sy*y), z)
        c0 = self.prj.forward(mapnik.Coord(p0[0],p0[1]))
        c1 = self.prj.forward(mapnik.Coord(p1[0],p1[1]))
        return mapnik.Envelope(c0.x,-c0.y,c1.x,-c1.y)

    def genTile(self, x, y, z, ext="png", cache=False):
        if cache:
            outname = '/home/sites/www.openhikingmaps.org/tiles/cache/%d/%d/%d.%s'%( z, x, y, ext)
            if os.path.exists(outname):
                fd = open(outname, 'r')
                return fd.read()
            try:
                os.makedirs(os.path.dirname(outname))
            except:
                pass
        else:
          outname = os.tmpnam()

        bbox = self.tileno2bbox(x, y, z)
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
