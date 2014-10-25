from flask import Flask
import json
from gen_tile import get_renderers
from osgeo import ogr
import mapnik

app = Flask(__name__)

renderers = get_renderers('styles', 16)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/tiles/<layer>/<int:z>/<int:x>/<int:y>.png')
def tile_render(layer, z, x, y):
    if layer in renderers:
        cache = False
        x = renderers[layer].genTile(x, y, z, 'png', cache)
        return x, 200, {
            'Content-Type': 'image/png',
            'Cache-Control': 'max-age=300'
        } 
    else:
       return "No Renderer for " + layer, 404

@app.route('/query/<layer>/<x>/<y>')
def query(layer, x, y):
    p = mapnik.Coord(float(x),float(y))

    # This needs to be wrapped in str() in order for 
    # it to be correctly passed to the C lib
    # NB: w/o str() and with it both have a type of str
    ogr_pt = str("POINT ("+x+" "+y+")")
    ogr_pt= ogr.Geometry(ogr.wkbUnknown, ogr_pt)

    feats = []

    has_seen = set()
    if layer in renderers:
        for l in renderers[layer].m.layers:
            print "Querying from " + l.name + " @ " + str(p)
            for feat in l.datasource.features_at_point(p):
                # features_at_point seems to use the bounding box
                # and/or a buffer for each feature. As a result the numbr
                # of features returned is much smaller than the whole set
                # but not exactly what I want.  As such, lets loop through
                # the filtered features and check if the click point is
                # really inside it
                go_forward = False
                for i in range(0, feat.num_geometries()):
                    # No idea why to_wkb dosn't work
                    geom = ogr.Geometry(ogr.wkbUnknown, feat.get_geometry(i).to_wkt())
                    go_forward = go_forward or geom.Intersects(ogr_pt)

                # If the point's really inside this feature, and we havn't
                # seen this feature before (my shp has duplicates?)
                if go_forward:
                    internal_id = l.name + "|" + feat.attributes['geoid']
                    if internal_id not in has_seen:
                        feats.append(json.loads(feat.to_geojson()))
                        has_seen.add(internal_id)
        return json.dumps(feats), 200, {
            'Content-Type': 'application/json',
            'Cache-Control': 'max-age=0'
        }
    else:
        return "No Renderer for " + layer, 404

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
    return app.send_static_file(path)


if __name__ == "__main__":
    app.debug = True
    app.run()
